"""
Mapa OSINERGMIN - Backend
==========================
Fuente de datos: Google Sheets (publicado como CSV), con caché en memoria
y respaldo en disco para resistir caídas o cortes de red temporales.

Variables de entorno (configurar en Render > Environment):
    GOOGLE_SHEET_ID        -> ID de la hoja de cálculo (obligatorio)
    GOOGLE_SHEET_GID        -> gid de la pestaña específica (opcional, default 0)
    CACHE_TTL_SECONDS       -> segundos antes de refrescar datos (default 600 = 10 min)
    ADMIN_TOKEN              -> token simple para proteger /actualizar (opcional pero recomendado)

Ver README.md para instrucciones paso a paso de cómo publicar el Google Sheet.
"""

from flask import Flask, jsonify, render_template, request
import pandas as pd
import os
import re
import json
import time
import threading
from io import StringIO
import requests

app = Flask(__name__)

# ==========================================================
# CONFIGURACIÓN
# ==========================================================
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "").strip()
GOOGLE_SHEET_GID = os.environ.get("GOOGLE_SHEET_GID", "0").strip()
CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "600"))
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")

CACHE_FILE = os.path.join(os.path.dirname(__file__), "cache", "ultimo_bueno.json")

_cache_lock = threading.Lock()
_cache = {
    "data": [],
    "last_update": None,     # epoch seconds del último refresco exitoso
    "last_error": None,
    "total": 0,
}


def _csv_url():
    if not GOOGLE_SHEET_ID:
        return None
    return (
        f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}"
        f"/export?format=csv&gid={GOOGLE_SHEET_GID}"
    )


# ==========================================================
# FUNCIONES AUXILIARES (igual que antes)
# ==========================================================
def extraer_numero(valor):
    if pd.isna(valor):
        return 0
    texto = str(valor).strip()
    if texto == "":
        return 0
    match = re.search(r"[-+]?\d*\.?\d+", texto.replace(",", ""))
    if match:
        try:
            return float(match.group())
        except Exception:
            return 0
    return 0


def texto_bonito(valor):
    if pd.isna(valor):
        return "0"
    t = str(valor).strip()
    if t == "":
        return "0"
    if not re.search(r"\d", t):
        return "0"
    return t


def _procesar_dataframe(df):
    df = df.rename(columns={
        "Razón Social": "razon",
        "Razon Social": "razon",

        "Registro de hidrocarburos": "registro",
        "Registro": "registro",

        "Código Osinergmin": "codigo",
        "Codigo Osinergmin": "codigo",

        "Actividad": "actividad",
        "Provincia": "provincia",
        "Distrito": "distrito",

        "Capacidad de almacenamiento": "capacidad",
        "Capacidad": "capacidad",

        "Estado del registro (Habilitado/Suspendido)": "estado",
        "Estado": "estado",

        "Ultima fiscalización": "fiscalizacion",
        "Última fiscalización": "fiscalizacion",

        "Longitud": "lng",
        "Latitud": "lat",

        "Capacidad total de GLP": "cap_total_glp",
        "Capacidad total GLP": "cap_total_glp",

        "Capacidad total CL": "cap_total_cl",
        "Capacidad total de CL": "cap_total_cl",

        "GLP en cilindros": "glp_cilindros",
        "GLP cilindros": "glp_cilindros",

        "Capacidad total GNV": "cap_total_gnv",
        "Capacidad total de GNV": "cap_total_gnv",

        "Dirección": "direccion",
    })

    df["lat"] = pd.to_numeric(df.get("lat"), errors="coerce")
    df["lng"] = pd.to_numeric(df.get("lng"), errors="coerce")

    for col in ["cap_total_glp", "cap_total_cl", "glp_cilindros", "cap_total_gnv"]:
        if col not in df.columns:
            df[col] = ""

    df["cap_total_glp_txt"] = df["cap_total_glp"].apply(texto_bonito)
    df["cap_total_cl_txt"] = df["cap_total_cl"].apply(texto_bonito)
    df["glp_cilindros_txt"] = df["glp_cilindros"].apply(texto_bonito)
    df["cap_total_gnv_txt"] = df["cap_total_gnv"].apply(texto_bonito)

    df["cap_total_glp"] = df["cap_total_glp"].apply(extraer_numero)
    df["cap_total_cl"] = df["cap_total_cl"].apply(extraer_numero)
    df["glp_cilindros"] = df["glp_cilindros"].apply(extraer_numero)
    df["cap_total_gnv"] = df["cap_total_gnv"].apply(extraer_numero)

    df["capacidad_total"] = (
        df["cap_total_glp"]
        + df["cap_total_cl"]
        + df["glp_cilindros"]
        + df["cap_total_gnv"]
    )
    df["capacidad_total"] = df["capacidad_total"].fillna(0)
    df.loc[df["capacidad_total"] <= 0, "capacidad_total"] = 1

    if "capacidad" in df.columns:
        df["capacidad"] = pd.to_numeric(df["capacidad"], errors="coerce").fillna(1)
    else:
        df["capacidad"] = df["capacidad_total"]

    df = df.dropna(subset=["lat", "lng"])

    return df.fillna("").to_dict(orient="records")


def _descargar_desde_google_sheets():
    url = _csv_url()
    if not url:
        raise RuntimeError(
            "GOOGLE_SHEET_ID no está configurado. Define la variable de entorno "
            "GOOGLE_SHEET_ID en Render (ver README.md)."
        )

    resp = requests.get(url, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Google Sheets respondió {resp.status_code}")

    resp.encoding = "utf-8"
    df = pd.read_csv(StringIO(resp.text))
    return _procesar_dataframe(df)


def _guardar_respaldo(data):
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        print("No se pudo guardar respaldo en disco:", e)


def _cargar_respaldo():
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _refrescar(force=False):
    """Refresca la caché en memoria si expiró (o si force=True)."""
    now = time.time()

    with _cache_lock:
        vigente = (
            _cache["last_update"] is not None
            and (now - _cache["last_update"]) < CACHE_TTL_SECONDS
        )
        if vigente and not force:
            return _cache

        try:
            data = _descargar_desde_google_sheets()
            _cache["data"] = data
            _cache["total"] = len(data)
            _cache["last_update"] = now
            _cache["last_error"] = None
            _guardar_respaldo(data)
            print(f"[cache] Datos actualizados: {len(data)} registros")
        except Exception as e:
            _cache["last_error"] = str(e)
            print("[cache] Error al refrescar:", e)

            # Si no hay nada en memoria todavía, intenta usar el respaldo en disco
            if not _cache["data"]:
                respaldo = _cargar_respaldo()
                if respaldo:
                    _cache["data"] = respaldo
                    _cache["total"] = len(respaldo)
                    print(f"[cache] Usando respaldo en disco: {len(respaldo)} registros")

        return _cache


# ==========================================================
# RUTAS
# ==========================================================
@app.route("/")
def index():
    return render_template("mapa.html")


@app.route("/datos")
def datos():
    c = _refrescar(force=False)
    return jsonify(c["data"])


@app.route("/estado")
def estado():
    c = _cache
    return jsonify({
        "total": c["total"],
        "last_update": c["last_update"],
        "last_error": c["last_error"],
        "cache_ttl_segundos": CACHE_TTL_SECONDS,
    })


@app.route("/actualizar", methods=["POST"])
def actualizar():
    if ADMIN_TOKEN:
        token = request.headers.get("X-Admin-Token", "")
        if token != ADMIN_TOKEN:
            return jsonify({"ok": False, "error": "No autorizado"}), 401

    c = _refrescar(force=True)
    return jsonify({
        "ok": c["last_error"] is None,
        "total": c["total"],
        "last_update": c["last_update"],
        "error": c["last_error"],
    })


# Refresca una vez al arrancar el servidor (usa respaldo si Sheets falla)
_refrescar(force=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
