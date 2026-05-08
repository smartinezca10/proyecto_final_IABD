# Eco-Scheduling Optimizer

Sistema inteligente de optimización de citas, rutas y precios dinámicos con enfoque ESG para servicios a domicilio.

El proyecto simula un escenario de servicios técnicos, sanitarios o estéticos a domicilio en el que el sistema propone precios dinámicos y alternativas de cita en función del impacto logístico, la demanda prevista, la distancia incremental y las emisiones estimadas de CO₂.

---

## 1. Objetivo del proyecto

El objetivo principal es desarrollar un prototipo funcional que combine:

- Optimización de rutas mediante VRP.
- Clustering geográfico de citas mediante DBSCAN.
- Predicción de demanda por zona, día y hora.
- Pricing dinámico basado en impacto logístico y ambiental.
- Visualización interactiva con Streamlit.
- Backend desacoplado mediante FastAPI.
- Pipeline de datos preparado para PySpark.

La idea central es el concepto de **Hueco de Eco-Servicio**: incentivar al cliente a elegir franjas horarias que reduzcan desplazamientos, kilómetros recorridos y emisiones de CO₂.

---

## 2. Tecnologías utilizadas

- Python 3.12
- uv para gestión de entorno y dependencias
- FastAPI
- Streamlit
- Pandas
- PySpark
- Scikit-learn
- OR-Tools
- Folium
- streamlit-folium
- OpenStreetMap / Nominatim
- Joblib
- PyArrow

---

## 3. Requisitos previos

Antes de ejecutar el proyecto, es necesario tener instalado:

- Python 3.12 recomendado.
- Java 11 o Java 17 para PySpark.
- uv instalado.
- Git.

Comprobar versiones:

```powershell
python --version
java -version
uv --version
```

---

## 4. Clonar el repositorio

```powershell
git clone https://github.com/smartinezca10/proyecto_final_IABD.git
cd proyecto_final_IABD
```

---

## 5. Crear y replicar el entorno

Como el proyecto incluye `pyproject.toml` y `uv.lock`, basta con ejecutar:

```powershell
uv sync
```

Si se desea crear el entorno manualmente:

```powershell
uv venv --python 3.11
uv sync
```

Dependencias principales usadas en el proyecto:

```powershell
uv add pandas numpy requests python-dotenv
uv add pyspark pyarrow setuptools
uv add scikit-learn joblib
uv add fastapi uvicorn pydantic
uv add streamlit folium streamlit-folium
uv add ortools
```

---

## 6. Estructura de directorios

```text
eco-scheduling-optimizer/
│
├── data/
│   ├── raw/                         # Datos simulados
│   └── processed/                   # Dataset procesado en Parquet
│
├── models/                          # Modelos entrenados
│   └── demand_model.pkl
│
├── src/
│   └── proyectoiabd/
│       │
│       ├── api/                     # Backend FastAPI
│       │   ├── main.py
│       │   ├── schemas.py
│       │   └── services.py
│       │
│       ├── clustering/              # Clustering geográfico
│       │   ├── dbscan_clustering.py
│       │   └── cluster_analysis.py
│       │
│       ├── config/                  # Configuración global
│       │   └── settings.py
│       │
│       ├── data_sources/            # Fuentes y generación de datos
│       │   ├── appointments_loader.py
│       │   ├── emissions_api.py
│       │   ├── generate_mock_data.py
│       │   ├── geolocation_api.py
│       │   └── streaming_simulator.py
│       │
│       ├── demand/                  # Modelo predictivo de demanda
│       │   ├── demand_model.py
│       │   └── demand_predictor.py
│       │
│       ├── features/                # Feature engineering
│       │   ├── feature_engineering.py
│       │   └── dbscan_clustering.py
│       │
│       ├── ingestion/               # Ingesta y limpieza
│       │   ├── batch_ingestion.py
│       │   ├── data_cleaning.py
│       │   └── streaming_ingestion.py
│       │
│       ├── pipelines/               # Pipelines batch
│       │   └── appointments_pipeline.py
│       │
│       ├── pricing/                 # Motor de pricing dinámico
│       │   ├── pricing_engine.py
│       │   └── green_score.py
│       │
│       ├── routing/                 # Optimización de rutas
│       │   ├── distance_matrix.py
│       │   ├── route_analysis.py
│       │   └── vrp_solver.py
│       │
│       ├── utils/                   # Utilidades generales
│       │   └── spark_session.py
│       │
│       ├── visualization/           # Dashboard Streamlit
│       │   └── streamlit_app.py
│       │
│       └── main.py                  # CLI para ejecutar pipeline batch
│
├── pyproject.toml
├── uv.lock
└── Readme.md
```

---

## 7. Flujo de ejecución completo

### 7.1 Generar datos simulados

El proyecto incluye un generador de citas sintéticas con demanda realista por zona, día y hora.

```powershell
uv run python src/proyectoiabd/data_sources/generate_mock_data.py
```

Esto genera:

```text
data/raw/appointments.csv
```

El generador contempla:

- Mayor demanda en Centro y Salamanca.
- Demanda media en Chamartín y Retiro.
- Menor demanda en Latina.
- Mayor actividad los lunes.
- Demanda media de martes a jueves.
- Menor actividad los viernes.
- Solo días laborables.
- Mayor demanda entre 09:00-13:00 y 17:00-19:00.

---

### 7.2 Ejecutar pipeline de datos

```powershell
uv run python src/proyectoiabd/main.py --mode pipeline
```

Este pipeline:

1. Carga el CSV de citas.
2. Limpia datos.
3. Genera variables temporales.
4. Guarda el dataset procesado.

Salida esperada:

```text
data/processed/appointments_features.parquet
```

---

### 7.3 Entrenar modelo de demanda

```powershell
uv run python src/proyectoiabd/demand/demand_model.py
```

Este modelo aprende patrones de demanda por:

- Zona.
- Día de la semana.
- Hora.

Salida esperada:

```text
models/demand_model.pkl
```

---

### 7.4 Lanzar backend FastAPI

En una terminal:

```powershell
uv run uvicorn proyectoiabd.api.main:app --reload
```

La documentación Swagger estará disponible en:

```text
http://127.0.0.1:8000/docs
```

Endpoint principal:

```text
POST /pricing/evaluate
```

Ejemplo de payload:

```json
{
  "latitude": 40.4168,
  "longitude": -3.7038,
  "zone": null,
  "hour": 10,
  "day_of_week": 2,
  "service_duration": 60
}
```

---

### 7.5 Lanzar dashboard Streamlit

En otra terminal:

```powershell
uv run streamlit run src/proyectoiabd/visualization/streamlit_app.py
```

Streamlit se abrirá normalmente en:

```text
http://localhost:8501
```

---

## 8. Funcionalidades principales

### 8.1 Solicitud de cita

La primera pestaña del dashboard permite:

- Seleccionar una ubicación de prueba.
- Elegir fecha dentro de los próximos días laborables.
- Elegir hora.
- Solicitar precio dinámico.
- Visualizar zona detectada.
- Ver precio, kilómetros incrementales y CO₂ estimado.
- Ver alternativas recomendadas por la empresa.

Las alternativas pueden ser:

- Slots verdes, si mejoran la eficiencia logística.
- Slots económicos, si mejoran el precio por demanda o disponibilidad.
- Sin alternativas, si no hay mejora relevante.

---

### 8.2 Detección de zonas no optimizables

El sistema detecta zonas donde no hay agrupación logística viable. En estos casos muestra un mensaje del tipo:

```text
No hay agrupación posible en tu zona porque se encuentra lejos de las áreas habituales de servicio.
```

Esto permite diferenciar entre:

- Mejora logística real.
- Mejora comercial por disponibilidad.
- Zonas lejanas o de alto impacto.

---

### 8.3 Clustering geográfico

La segunda pestaña permite analizar los clusters de citas mediante DBSCAN.

Se visualizan:

- Puntos de citas.
- Clusters por color.
- Centros de agrupación.
- Ruido o citas aisladas.
- KPIs de número de citas, clusters y puntos no agrupados.

---

### 8.4 Explorador de datos

El dashboard incluye un visor paginado del dataset procesado:

- Registros por página.
- Navegación por páginas.
- Vista de detalle de cada registro.

---

## 9. Algoritmos y modelos incluidos

### 9.1 DBSCAN

Se utiliza DBSCAN para detectar zonas de alta densidad geográfica sin necesidad de definir previamente el número de clusters.

Ventajas:

- Detecta agrupaciones naturales.
- Identifica ruido.
- Es adecuado para datos urbanos irregulares.

---

### 9.2 Distancia Haversine

Para calcular distancias entre coordenadas se usa la fórmula de Haversine.

Se utiliza para construir matrices de distancia entre citas.

---

### 9.3 Estimación de CO₂

El impacto ambiental se calcula mediante un factor de emisión simplificado:

```text
CO₂ = distancia_km × factor_emisión
```

En el prototipo se utiliza un factor estático para mantener la reproducibilidad.

---

### 9.4 Modelo predictivo de demanda

Se entrena un Random Forest Regressor para estimar la demanda esperada a partir de:

- Zona.
- Hora.
- Día de la semana.

El modelo no predice una fecha exacta de calendario, sino un patrón semanal esperado.

---

### 9.5 Pricing dinámico

El motor de pricing evalúa:

- Impacto en kilómetros.
- Impacto en CO₂.
- Encaje con rutas existentes.
- Demanda prevista.
- Posibilidad de ofrecer alternativas.

El sistema diferencia entre:

- Green Slot.
- Light Green Slot.
- High Impact Slot.
- Zona no optimizable.

---

## 10. Consideraciones sobre OpenStreetMap

El sistema usa OpenStreetMap/Nominatim para hacer reverse geocoding, es decir, obtener una zona textual aproximada a partir de latitud y longitud.

En algunos casos, OpenStreetMap puede devolver barrios o microzonas distintas a las zonas del modelo. Por este motivo, el proyecto utiliza una lista de ubicaciones de prueba y lógica de negocio simplificada para mantener la coherencia en la demo.

En una versión productiva se recomienda usar PostGIS o una tabla propia de polígonos de zonas de servicio.

---


## 11. Orden recomendado para ejecución

```powershell
# 1. Generar datos
uv run python src/proyectoiabd/data_sources/generate_mock_data.py

# 2. Ejecutar pipeline
uv run python src/proyectoiabd/main.py --mode pipeline

# 3. Entrenar demanda
uv run python src/proyectoiabd/demand/demand_model.py

# 4. Lanzar API
uv run uvicorn proyectoiabd.api.main:app --reload

# 5. Lanzar Streamlit
uv run streamlit run src/proyectoiabd/visualization/streamlit_app.py
```

---

## 12. Posibles mejoras futuras

- Integración con PostGIS.
- Uso de rutas reales mediante OSRM o Google Maps API.
- Uso de APIs de cálculo de huella de carbono
- Predicción de demanda por fecha concreta.
- Optimización multi-vehículo.
- Integración con calendarios reales.
- Despliegue en cloud.
- Monitorización con métricas operativas.
- Añadir autenticación y roles de usuario.
- Incorporar festivos y disponibilidad real de técnicos.

---

## 13. Autor

Proyecto desarrollado como Proyecto Final del Curso de Especialización en Inteligencia Artificial y Big Data.

Autor: **Sergio Martínez Castaño**

Centro: **Davante/MEDAC**

Curso académico: **2026**
