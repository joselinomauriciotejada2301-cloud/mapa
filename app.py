from flask import Flask, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# ===== CONFIGURACIÓN =====
EXCEL_PATH = "Datosmapa.xlsx"

# ===== CARGA DE DATOS =====
def cargar_datos():
    df = pd.read_excel(EXCEL_PATH)

    df = df.rename(columns={
        "Razón Social": "razon",
        "Razon Social": "razon",
        "Registro de hidrocarburos": "registro",
        "Código Osinergmin": "codigo",
        "Codigo Osinergmin": "codigo",
        "Actividad": "actividad",
        "Ubigeo (Dirección)": "direccion",
        "Provincia": "provincia",
        "Distrito": "distrito",
        "Capacidad de almacenamiento": "capacidad",
        "Estado del registro (Habilitado/Suspendido)": "estado",
        "Ultima fiscalización": "fiscalizacion",
        "Longitud": "lng",
        "Latitud": "lat"
    })

    # Limpiar coordenadas vacías
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
    df = df.dropna(subset=["lat", "lng"])

    return df.to_dict(orient="records")


@app.route("/")
def index():
    return render_template("mapa.html")


@app.route("/datos")
def datos():
    return jsonify(cargar_datos())


if __name__ == "__main__":
    print("✅ Servidor iniciado")
    print("🌎 Abre en tu navegador: http://127.0.0.1:5000")
    app.run(debug=True)

