# Mapa OSINERGMIN — versión optimizada

Mapa interactivo de agentes de hidrocarburos. Esta versión reemplaza Google Maps
por **Leaflet + OpenStreetMap/CARTO** (100% gratis, sin API key, sin facturación,
sin límites de cuota) y reemplaza el link personal de SharePoint por una
**hoja de Google Sheets** que tú mismo puedes editar como si fuera un Excel en línea.

## Qué cambió respecto a la versión anterior

| Antes | Ahora |
|---|---|
| Google Maps JS API con key expuesta en el HTML público | Leaflet + teselas CARTO/OSM, sin key, sin facturación |
| Se agotaba la cuota gratuita y había que crear cuentas nuevas | No existe cuota que agotar |
| Excel descargado de un link personal de SharePoint en cada visita | Google Sheets publicado, con caché de 10 min en el backend |
| Sin caché → cada visita descargaba el Excel entero | Caché en memoria + respaldo en disco (`cache/ultimo_bueno.json`) |
| Heatmap roto (`alert("Google eliminó HeatmapLayer...")`) | Heatmap funcional con Leaflet.heat |
| Miles de marcadores sueltos (lento con más datos) | Agrupados en clusters (Leaflet.markercluster), más rápido |
| Servidor de desarrollo de Flask en producción | Gunicorn (servidor de producción) vía `Procfile` |

Todas las funcionalidades originales se mantienen: buscador por código/razón social
(incluye búsqueda múltiple), búsqueda por coordenadas con radio ajustable, medición
de distancia, resaltado de distritos (uno o varios), filtros por estado/actividad/
provincia/distrito/año, y estadísticas por actividad y distrito.

---

## 1. Configurar tu "Excel en línea" (Google Sheets)

1. Ve a [Google Sheets](https://sheets.google.com) y crea una hoja nueva.
2. Importa tu Excel actual: **Archivo → Importar → Subir** tu `Datosmapa.xlsx`,
   eligiendo "Reemplazar la hoja de cálculo actual".
3. Verifica que las columnas se llamen igual que en tu Excel original (Razón Social,
   Registro de hidrocarburos, Código Osinergmin, Actividad, Dirección, Provincia,
   Distrito, Estado del registro (Habilitado/Suspendido), Ultima fiscalización,
   Longitud, Latitud, Capacidad total de GLP, Capacidad total CL, GLP en cilindros,
   Capacidad total GNV). El backend ya reconoce esos nombres automáticamente.
4. Comparte la hoja: botón **Compartir → Cambiar a "Cualquier persona con el
   enlace"** con permiso de **Lector** (no editor, así nadie externo puede
   modificar tus datos, solo verlos).
5. Copia el ID de la hoja desde la URL:
   `https://docs.google.com/spreadsheets/d/`**`ESTE_ES_EL_ID`**`/edit#gid=0`
6. Si tus datos están en una pestaña que no es la primera, copia también el
   número que aparece después de `gid=` en la URL.

De ahí en adelante, **cada vez que edites o subas datos nuevos a esa hoja**,
el mapa los reflejará automáticamente (dentro de los 10 minutos de caché, o
al instante si usas el botón "Actualizar datos ahora" del panel izquierdo).

## 2. Configurar variables de entorno en Render

En tu servicio de Render → **Settings → Environment**, agrega:

| Variable | Valor |
|---|---|
| `GOOGLE_SHEET_ID` | el ID que copiaste en el paso anterior |
| `GOOGLE_SHEET_GID` | el gid de la pestaña (déjalo en `0` si no tienes varias pestañas) |
| `CACHE_TTL_SECONDS` | `600` (10 minutos; súbelo si quieres refrescar con menos frecuencia) |

Elimina cualquier referencia a `EXCEL_URL` que hubiera quedado de la versión anterior.

## 3. Desplegar

Este repo ya incluye un `Procfile` (`web: gunicorn app:app ...`), así que Render lo
detecta automáticamente como comando de inicio. Solo necesitas:

1. Reemplazar el contenido de tu repo de GitHub por los archivos de este proyecto.
2. Verificar en Render que el "Start Command" esté vacío (para que use el `Procfile`)
   o que sea exactamente `gunicorn app:app`.
3. Hacer *Manual Deploy* o esperar el auto-deploy del push.

No necesitas ninguna API key, ni cuenta de facturación, ni volver a crear cuentas.

## 4. Estructura del proyecto

```
app.py                      Backend Flask (Google Sheets + caché)
requirements.txt
Procfile                    Comando de arranque en producción (gunicorn)
templates/mapa.html         Frontend (Leaflet, sin dependencias de pago)
static/distritos.geojson.json
static/vendor/              Leaflet y plugins empaquetados localmente (sin CDN externo)
cache/ultimo_bueno.json     Respaldo automático del último dato bueno descargado
```

## 5. Endpoints del backend

- `GET /` — página del mapa
- `GET /datos` — JSON con los registros (usa caché, se refresca cada `CACHE_TTL_SECONDS`)
- `GET /estado` — última actualización, total de registros y último error si lo hubo
- `POST /actualizar` — fuerza un refresco inmediato desde Google Sheets (lo dispara
  el botón "Actualizar datos ahora" del panel izquierdo)

## 6. Notas sobre el mapa base (teselas)

Se usan teselas gratuitas de CARTO (basadas en datos de OpenStreetMap), sin
necesidad de key. Son adecuadas para uso institucional moderado. Si en el futuro
el tráfico crece mucho y buscas más garantías de nivel de servicio, existen
alternativas económicas como MapTiler o Stadia Maps (tienen capa gratuita y
planes pagos mucho más baratos que Google Maps), o mantener CARTO/OSM tal como
está — para uso interno de OSINERGMIN esto no debería ser un problema.
