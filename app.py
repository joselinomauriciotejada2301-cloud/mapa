from flask import Flask, jsonify, render_template
import pandas as pd
import os

app = Flask(__name__)

EXCEL_PATH = "Datosmapa.xlsx"

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
    # CONVERTIR CAPACIDADES NUEVAS
    # ==========================================================
    for col in ["cap_total_glp", "cap_total_cl", "glp_cilindros", "cap_total_gnv"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

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
        # Si ya no existe, la creamos por compatibilidad
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
