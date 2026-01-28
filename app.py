from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# ========================
# CONFIGURACIÓN
# ========================

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

# ============================
# LISTA DE ACTIVIDADES VÁLIDAS
# ============================

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
"074-LOCALES DE VENTA DE GLP EN CILINDROS CON CAPACIDAD MENOR O IGUAL A 5,000 KG",
"078-LOCALES DE VENTA DE GLP EN CILINDROS CON CAPACIDAD MAYOR A 5,000 KG",
"101-CONSUMIDOR DIRECTO DE GNV",
"102-ESTABLECIMIENTO DE VENTA AL PUBLICO DE GNV",
"106-EE.SS con GNV",
"107-EE.SS con GLP y GNV",
"112-CONSUMIDOR DIRECTO DE OPDH Y COMBUSTIBLE LÍQUIDO CON CAPACIDAD HASTA 5 MB",
"114-CONSUMIDOR DIRECTO DE OPDH Y COMBUSTIBLE LÍQUIDO CON CAPACIDAD DE 5 A 50 MB",
"115-CONSUMIDORES DIRECTOS DE OTROS PRODUCTOS DERIVADOS DE LOS HIDROCARBUROS",
"190-ESTABLECIMIENTO DESTINADO AL SUMINISTRO DE GNV EN SISTEMAS INTEGRADOS DE TRANSPORTE",
"300-PROCES GNL",
"320-GASOCENTRO DE GLP CON ESTABLECIMIENTO DE VENTA AL PUBLICO DE GNV",
"400-CONSUMIDORES DIRECTOS DE GLP CON CAPACIDAD MENOR O IGUAL A 1000 GLN",
"401-CONSUMIDORES DIRECTOS DE GLP CON CAPACIDAD MAYOR A 1000 GLN",
"600-REDES DE DISTRIBUCIÓN DE GLP CON CAPACIDAD MENOR O IGUAL A 1000 GLN",
"601-REDES DE DISTRIBUCIÓN DE GLP CON CAPACIDAD MAYOR A 1000 GLN",
"607-ESTACION DE COMPRESIÓN DE GAS NATURAL",
"613-ESTACIÓN DE CARGA DE GNL",
"618-ESTACIÓN DE CARGA DE GNC",
"975-CONSUMIDORES DIRECTOS CON INSTALACIONES ESTRATEGICAS",
"982-CONSUMIDOR DIRECTO CON INSTALACIONES ESTRATEGICAS DE GLP CON CAPACIDAD MAYOR A 1000 GLN",
"983-CONSUMIDOR DIRECTO CON INSTALACIONES ESTRATEGICAS TEMPORALES",
"984-CONSUMIDOR DIRECTO CON INSTALACIONES ESTRATEGICAS DE GLP CON CAPACIDAD MENOR O IGUAL A 1000 GLN"
]

# ========================
# CARGA DE DATOS
# ========================

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

# ========================
# INICIO SERVIDOR
# ========================

if __name__ == "__main__":
    app.run()






