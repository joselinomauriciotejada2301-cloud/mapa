from flask import Flask, jsonify, render_template
import pandas as pd
import os

app = Flask(__name__)

EXCEL_PATH = "Datosmapa.xlsx"

def cargar_datos():
    df = pd.read_excel(EXCEL_PATH)

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
        "Latitud": "lat"
    })

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
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












