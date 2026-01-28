from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

EXCEL_PATH = "Datosmapa.xlsx"

COLUMN_MAPPING = {
    "Razón Social": "razon",
    "Razon Social": "razon",
    "Registro de hidrocarburos": "registro",
    "Código Osinergmin": "codigo",
    "Codigo Osinergmin": "codigo",
    "Actividad": "actividad",
    "Provincia": "provincia",
    "Distrito": "distrito",
    "Capacidad de almacenamiento": "capacidad",
    "Estado del registro (Habilitado/Suspendido)": "estado",
    "Ultima fiscalización": "fiscalizacion",
    "Longitud": "lng",
    "Latitud": "lat"
}

ACTIVIDADES_VALIDAS = [
"030-REFINERIAS TOPPING",
"034-PLANTAS LUBRICANTES Y GRASAS",
"040-PLANTA DE ABASTECIMIENTO DE COMBUSTIBLES LIQUIDOS",
"050-ESTACIÓN DE SERVICIOS / GRIFOS",
"051-CONSUMIDOR DIRECTO DE COMBUSTIBLE LÍQUIDO CON CAPACIDAD HASTA 5 MB",
"052-CONSUMIDOR DIRECTO DE COMBUSTIBLE LÍQUIDO CON CAPACIDAD DE 5  A 50 MB",
"053-CONSUMIDOR DIRECTO DE COMBUSTIBLE LÍQUIDO CON CAPACIADAD MAYOR A 50 MB",
"056-ESTACIÓN DE SERVICIO CON GASOCENTRO DE GLP",
"070-PLANTAS ENVASADORAS GLP",
"071-GASOCENTROS DE GLP",
"074-LOCALES DE VENTA DE GLP EN CILINDROS ≤ 5,000 KG",
"078-LOCALES DE VENTA DE GLP EN CILINDROS > 5,000 KG",
"101-CONSUMIDOR DIRECTO DE GNV",
"102-ESTABLECIMIENTO DE VENTA AL PUBLICO DE GNV",
"106-EE.SS con GNV",
"107-EE.SS con GLP y GNV",
"112-CONSUMIDOR DIRECTO DE OPDH Y COMBUSTIBLE LÍQUIDO HASTA 5 MB",
"114-CONSUMIDOR DIRECTO DE OPDH Y COMBUSTIBLE LÍQUIDO DE 5 A 50 MB",
"115-CONSUMIDORES DIRECTOS DE OTROS PRODUCTOS",
"190-SUMINISTRO GNV SISTEMA INTEGRADO",
"300-PROCES GNL",
"320-GASOCENTRO GLP + VENTA GNV",
"400-CONSUMIDOR DIRECTO GLP ≤1000 GLN",
"401-CONSUMIDOR DIRECTO GLP >1000 GLN",
"600-RED DISTRIBUCIÓN GLP ≤1000 GLN",
"601-RED DISTRIBUCIÓN GLP >1000 GLN",
"607-ESTACION COMPRESION GAS NATURAL",
"613-ESTACION CARGA GNL",
"618-ESTACION CARGA GNC",
"975-CONSUMIDOR DIRECTO INSTALACION ESTRATEGICA",
"982-CONSUMIDOR DIRECTO ESTRATEGICA GLP >1000 GLN",
"983-CONSUMIDOR DIRECTO ESTRATEGICA TEMPORAL",
"984-CONSUMIDOR DIRECTO ESTRATEGICA GLP ≤1000 GLN"
]

def cargar_datos():
    df = pd.read_excel(EXCEL_PATH)
    df = df.rename(columns=COLUMN_MAPPING)
    df = df.dropna(subset=["lat", "lng"])
    df["actividad"] = df["actividad"].astype(str).str.strip()
    df = df[df["actividad"].isin(ACTIVIDADES_VALIDAS)]
    return df

@app.route("/")
def index():
    return render_template("mapa.html")

@app.route("/datos")
def datos():
    df = cargar_datos()
    return df.to_json(orient="records", force_ascii=False)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)








