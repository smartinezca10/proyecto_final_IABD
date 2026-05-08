import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import date, timedelta

from proyectoiabd.clustering.dbscan_clustering import run_dbscan
from proyectoiabd.clustering.cluster_analysis import compute_cluster_centers

import requests
import random


def draw_route(map_obj, df, route):
    for i in range(len(route) - 1):
        p1 = df.iloc[route[i]]
        p2 = df.iloc[route[i + 1]]

        folium.PolyLine(
            locations=[
                [p1['latitude'], p1['longitude']],
                [p2['latitude'], p2['longitude']]
            ],
            color="blue",
            weight=3
        ).add_to(map_obj)

def get_next_date_for_weekday(base_date: date, target_weekday: int) -> date:
    """
    Devuelve la fecha más cercana, igual o posterior a base_date,
    que coincide con target_weekday.
    """
    days_ahead = (target_weekday - base_date.weekday()) % 7
    return base_date + timedelta(days=days_ahead)

st.set_page_config(layout="wide")

st.title("🌱 Eco-Scheduling Optimizer - Clustering Geográfico")

# --------------------------
# Tabs
# --------------------------
tab1, tab2 = st.tabs(["💰 Solicitar cita", "🗺️ Clustering & Análisis"])


# --------------------------
# Cargar datos
# --------------------------
@st.cache_data
def load_data():
    df = pd.read_parquet("data/processed/appointments_features.parquet")
    return df


@st.cache_data
def get_clustered_data(df, eps_km, min_samples):
    return run_dbscan(df.copy(), eps_km, min_samples)


df = load_data()


# ==========================================================
# TAB 1 → PRICING (CLIENTE)
# ==========================================================
with tab1:

    st.subheader("💰 Pricing dinámico vía FastAPI")

    api_url = "http://127.0.0.1:8000/pricing/evaluate"


    # --------------------------
    # Selector de ubicaciones de prueba
    # --------------------------
    TEST_LOCATIONS = {
        "Centro - Puerta del Sol / zona muy saturada": {
            "lat": 40.416947,
            "lon": -3.703528,
        },
        "Centro - Gran Vía / alta probabilidad de Green Slot": {
            "lat": 40.420300,
            "lon": -3.705770,
        },
        "Salamanca - Goya / zona premium alta demanda": {
            "lat": 40.425900,
            "lon": -3.676800,
        },
        "Salamanca - Lista / zona densa y comercial": {
            "lat": 40.432900,
            "lon": -3.675900,
        },
        "Chamartín - Prosperidad / buena cobertura": {
            "lat": 40.444900,
            "lon": -3.674500,
        },
        "Chamartín - Nueva España / demanda media-alta": {
            "lat": 40.461900,
            "lon": -3.677700,
        },
        "Retiro - Ibiza / zona residencial con demanda media": {
            "lat": 40.418200,
            "lon": -3.676800,
        },
        "Retiro - Niño Jesús / demanda media-baja": {
            "lat": 40.410600,
            "lon": -3.669100,
        },
        "Latina - Aluche / zona menos saturada": {
            "lat": 40.392700,
            "lon": -3.760800,
        },
        "Latina - Puerta del Ángel / menor densidad de citas": {
            "lat": 40.413700,
            "lon": -3.729300,
        },
        "Alcobendas - petición lejana norte / alto impacto Ecológico": {
            "lat": 40.541500,
            "lon": -3.626300,
        },
        "Getafe - El Carrascal / alto impacto Ecológico": {
            "lat": 40.329500,
            "lon": -3.736500,
        }
    }
    selected_location = st.selectbox(
        "Ubicación de prueba",
        list(TEST_LOCATIONS.keys()),
        index=0
    )

    selected_coords = TEST_LOCATIONS[selected_location]

    lat = st.number_input(
        "Latitud",
        value=float(selected_coords["lat"]),
        format="%.6f"
    )

    lon = st.number_input(
        "Longitud",
        value=float(selected_coords["lon"]),
        format="%.6f"
    )

    hour = st.slider("Hora", 8, 20, 10)
    # --------------------------
    # Selector de fecha (7 días laborables)
    # --------------------------
    today = date.today()

    available_dates = []
    current_date = today

    while len(available_dates) < 7:
        # weekday(): lunes=0, domingo=6
        if current_date.weekday() <= 4:
            available_dates.append(current_date)

        current_date += timedelta(days=1)


    def format_date(d):
        day_names = {
            0: "Lunes",
            1: "Martes",
            2: "Miércoles",
            3: "Jueves",
            4: "Viernes",
        }

        return f"{day_names[d.weekday()]} {d.strftime('%d/%m/%Y')}"


    selected_date = st.selectbox(
        "Fecha de la cita",
        available_dates,
        format_func=format_date,
        index=0
    )

    day_of_week = selected_date.weekday()

    st.caption(
        "Los precios dinámicos se ofrecen para los próximos 7 días laborables. "
        "La demanda se estima a partir de patrones históricos por zona, día de la semana y hora."
    )

    if st.button("Calcular precio dinámico"):
        payload = {
            "latitude": lat,
            "longitude": lon,
            "zone": None,
            "hour": hour,
            "day_of_week": day_of_week,
            "service_duration": 60
        }

        response = requests.post(api_url, json=payload)

        if response.status_code == 200:
            result = response.json()

            requested = result["requested_option"]
            st.write(f"📍 Zona detectada: {requested.get('zone', 'No disponible')}")
            alternatives = result["alternative_options"]

            if result.get("non_optimizable_zone"):
                st.warning(result.get("message"))

            st.markdown("### 📌 Opción solicitada por el cliente")

            col1, col2, col3 = st.columns(3)

            col1.metric("Precio", f"{requested['price']} €")
            col2.metric("Δ km", requested["delta_km"])
            col3.metric("Δ CO₂", requested["delta_co2"])

            st.success(requested["label"])
            st.write(requested["explanation"])

            st.markdown("### 💡 Alternativas recomendadas por la empresa")

            day_names = {
                0: "Lunes",
                1: "Martes",
                2: "Miércoles",
                3: "Jueves",
                4: "Viernes",
                5: "Sábado",
                6: "Domingo"
            }

            if not alternatives:
                st.info(
                    "No se han encontrado alternativas que mejoren de forma relevante "
                    "el precio o el impacto logístico/ambiental de la cita solicitada."
                )
            else:
                for i, option in enumerate(alternatives, start=1):
                    alternative_date = get_next_date_for_weekday(
                        selected_date,
                        option["day_of_week"]
                    )

                    st.markdown(
                        f"#### Alternativa {i}: {day_names[option['day_of_week']]} "
                        f"{alternative_date.strftime('%d/%m/%Y')} "
                        f"a las {option['hour']}:00"
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric("Precio", f"{option['price']} €")
                    col2.metric("Δ km", option["delta_km"])
                    col3.metric("Δ CO₂", option["delta_co2"])

                    st.info(option["label"])
                    st.write(option["explanation"])
                    st.caption(
                        f"Fecha propuesta: {alternative_date.strftime('%d/%m/%Y')}"
                    )
        else:
            st.error("Error llamando a FastAPI")
            st.write(response.text)


# ==========================================================
# TAB 2 → CLUSTERING (ANÁLISIS)
# ==========================================================
with tab2:

    st.subheader("⚙️ Configuración de clustering")

    # Configuración de clustering
    eps_km = st.slider("Radio cluster (km)", 0.1, 2.0, 0.5)
    min_samples = st.slider("Min puntos cluster", 2, 10, 5)

    # --------------------------
    # Clustering
    # --------------------------
    df_clustered = get_clustered_data(df, eps_km, min_samples)
    centers = compute_cluster_centers(df_clustered)

    # --------------------------
    # Visor paginado
    # --------------------------
    st.subheader("📋 Explorador de citas procesadas")

    with st.expander("Ver dataset procesado", expanded=False):

        total_rows = len(df_clustered)

        page_size = st.selectbox(
            "Registros por página",
            options=[10, 25, 50, 100],
            index=1
        )

        total_pages = max((total_rows - 1) // page_size + 1, 1)

        page = st.number_input(
            "Página",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1
        )

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        st.caption(
            f"Mostrando registros {start_idx + 1} - {min(end_idx, total_rows)} de {total_rows}"
        )

        st.dataframe(
            df_clustered.iloc[start_idx:end_idx],
            width='stretch',
            height=400
        )

        selected_index = st.number_input(
            "Ver detalle del registro número",
            min_value=0,
            max_value=total_rows - 1,
            value=0,
            step=1
        )

        selected_row = df_clustered.iloc[selected_index]

        st.markdown("### 🔎 Detalle del registro seleccionado")
        st.json(selected_row.to_dict())

        # --------------------------
        # Simulación pricing
        # --------------------------
        st.subheader("💰 Simulación de Pricing Dinámico")

        if st.button("Simular nueva cita verde"):

            sample_df = df_clustered[df_clustered["cluster"] == 0].head(10)

            if sample_df.empty:
                st.warning("No hay citas suficientes en el cluster 0.")
            else:
                base = sample_df.iloc[0]

                payload = {
                    "latitude": float(base["latitude"] + random.uniform(-0.01, 0.01)),
                    "longitude": float(base["longitude"] + random.uniform(-0.01, 0.01)),
                    "zone": str(base.get("zone", "Centro")),
                    "hour": int(hour),
                    "day_of_week": int(day_of_week),
                    "service_duration": 60
                }

                response = requests.post(
                    "http://127.0.0.1:8000/pricing/evaluate",
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()

                    col1, col2, col3 = st.columns(3)

                    requested = result["requested_option"]

                    col1.metric("Precio dinámico", f"{requested['price']} €")
                    col2.metric("Δ km", requested["delta_km"])
                    col3.metric("Δ CO₂", requested["delta_co2"])

                    st.success(requested["label"])
                    st.write(requested["explanation"])
                    st.json(result)
                else:
                    st.error("Error llamando al backend FastAPI")
                    st.write(response.text)

    # --------------------------
    # Mapa
    # --------------------------
    st.subheader("🗺️ Mapa de Clusters")

    def get_cluster_color(cluster_id):
        if cluster_id == -1:
            return "gray"

        colors = [
            "red", "blue", "green", "purple", "orange",
            "darkred", "lightred", "beige", "darkblue",
            "darkgreen", "cadetblue", "darkpurple", "pink",
            "lightblue", "lightgreen", "black"
        ]

        return colors[int(cluster_id) % len(colors)]

    center_map = [df["latitude"].mean(), df["longitude"].mean()]
    m = folium.Map(location=center_map, zoom_start=12)

    for _, row in df_clustered.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=4,
            color=get_cluster_color(row["cluster"]),
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

    for _, row in centers.iterrows():
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(m)

    st_folium(m, width=1200, height=600, returned_objects=[])

    # --------------------------
    # KPIs
    # --------------------------
    st.subheader("📊 Métricas")

    total_points = len(df_clustered)
    num_clusters = df_clustered['cluster'].nunique() - (1 if -1 in df_clustered['cluster'].values else 0)
    noise_points = len(df_clustered[df_clustered['cluster'] == -1])

    col1, col2, col3 = st.columns(3)

    col1.metric("Total citas", total_points)
    col2.metric("Clusters detectados", num_clusters)
    col3.metric("Ruido (no agrupado)", noise_points)

    # --------------------------
    # ESG
    # --------------------------
    st.subheader("🌱 Interpretación ESG")

    st.markdown("""
    - Los clusters representan **zonas eficientes de servicio**
    - Cuantos más puntos en un cluster → menos desplazamientos
    - El ruido representa citas aisladas (alto impacto CO₂)

    👉 Este mapa permite identificar "Green Slots"
    """)