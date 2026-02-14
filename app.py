from flask import Flask, jsonify, render_template
import pandas as pd
import os
import re

app = Flask(__name__)

EXCEL_PATH = "Datosmapa.xlsx"


# ==========================================================
# FUNCIONES AUXILIARES
# ==========================================================
def extraer_numero(valor):
    """
    Convierte:
    '480 kg' -> 480
    '2000 LITROS' -> 2000
    'GALONES' -> 0
    '' -> 0
    None -> 0
    """
    if pd.isna(valor):
        return 0

    texto = str(valor).strip()

    if texto == "":
        return 0

    # Busca el primer número (entero o decimal)
    match = re.search(r"[-+]?\d*\.?\d+", texto.replace(",", ""))
    if match:
        try:
            return float(match.group())
        except:
            return 0

    return 0


def texto_bonito(valor):
    """
    Devuelve texto listo para mostrar en popup:
    - Si está vacío -> '0'
    - Si es numérico -> '480'
    - Si es texto con unidad -> '480 kg'
    - Si es 'GALONES' -> '0'
    """
    if pd.isna(valor):
        return "0"

    t = str(valor).strip()
    if t == "":
        return "0"

    # Si no tiene ningún número, devolvemos 0
    if not re.search(r"\d", t):
        return "0"

    return t


def cargar_datos():
    df = pd.read_excel(EXCEL_PATH)

    # ==========================================================
    # RENOMBRAR COLUMNAS (INCLUYENDO LAS NUEVAS)
    # ==========================================================
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

        # ⚠️ Ya no existe "Capacidad de almacenamiento"
        # pero lo dejamos por compatibilidad si aparece en algún Excel viejo
        "Capacidad de almacenamiento": "capacidad",
        "Capacidad": "capacidad",

        "Estado del registro (Habilitado/Suspendido)": "estado",
        "Estado": "estado",

        "Ultima fiscalización": "fiscalizacion",
        "Última fiscalización": "fiscalizacion",

        "Longitud": "lng",
        "Latitud": "lat",

        # ======================================================
        # NUEVAS COLUMNAS
        # ======================================================
        "Capacidad total de GLP": "cap_total_glp",
        "Capacidad total GLP": "cap_total_glp",

        "Capacidad total CL": "cap_total_cl",
        "Capacidad total de CL": "cap_total_cl",

        "GLP en cilindros": "glp_cilindros",
        "GLP cilindros": "glp_cilindros",

        "Capacidad total GNV": "cap_total_gnv",
        "Capacidad total de GNV": "cap_total_gnv"
    })

    # ==========================================================
    # CONVERTIR COORDENADAS
    # ==========================================================
    df["lat"] = pd.to_numeric(df.get("lat"), errors="coerce")
    df["lng"] = pd.to_numeric(df.get("lng"), errors="coerce")

    # ==========================================================
    # ASEGURAR COLUMNAS NUEVAS
    # ==========================================================
    for col in ["cap_total_glp", "cap_total_cl", "glp_cilindros", "cap_total_gnv"]:
        if col not in df.columns:
            df[col] = ""

    # ==========================================================
    # GUARDAR VERSION TEXTO (BONITA) PARA POPUP
    # ==========================================================
    df["cap_total_glp_txt"] = df["cap_total_glp"].apply(texto_bonito)
    df["cap_total_cl_txt"] = df["cap_total_cl"].apply(texto_bonito)
    df["glp_cilindros_txt"] = df["glp_cilindros"].apply(texto_bonito)
    df["cap_total_gnv_txt"] = df["cap_total_gnv"].apply(texto_bonito)

    # ==========================================================
    # CONVERTIR CAPACIDADES A NUMERO (PARA HEATMAP)
    # ==========================================================
    df["cap_total_glp"] = df["cap_total_glp"].apply(extraer_numero)
    df["cap_total_cl"] = df["cap_total_cl"].apply(extraer_numero)
    df["glp_cilindros"] = df["glp_cilindros"].apply(extraer_numero)
    df["cap_total_gnv"] = df["cap_total_gnv"].apply(extraer_numero)

    # ==========================================================
    # CAPACIDAD TOTAL (PARA HEATMAP)
    # ==========================================================
    df["capacidad_total"] = (
        df["cap_total_glp"]
        + df["cap_total_cl"]
        + df["glp_cilindros"]
        + df["cap_total_gnv"]
    )

    # Si por algún motivo capacidad_total queda en 0, le damos 1 para que el heatmap no se "muera"
    df["capacidad_total"] = df["capacidad_total"].fillna(0)
    df.loc[df["capacidad_total"] <= 0, "capacidad_total"] = 1

    # ==========================================================
    # (COMPATIBILIDAD) SI EXISTE "capacidad" AÚN, CONVERTIRLA
    # ==========================================================
    if "capacidad" in df.columns:
        df["capacidad"] = pd.to_numeric(df["capacidad"], errors="coerce").fillna(1)
    else:
        df["capacidad"] = df["capacidad_total"]

    # ==========================================================
    # ELIMINAR REGISTROS SIN COORDENADAS
    # ==========================================================
    df = df.dropna(subset=["lat", "lng"])

    return df.fillna("").to_dict(orient="records")


@app.route("/")
def index():
    return render_template("mapa.html")


@app.route("/datos")
def datos():
    return jsonify(cargar_datos())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
