import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from pathlib import Path


# --------------------------
# CONFIG
# --------------------------
NUM_SAMPLES = 2000
OUTPUT_PATH = "data/raw/appointments.csv"

# Centros de Madrid + peso de demanda por zona
ZONES = {
    "Centro": {
        "coords": (40.4168, -3.7038),
        "weight": 1.35,
    },
    "Salamanca": {
        "coords": (40.4300, -3.6800),
        "weight": 1.20,
    },
    "Chamartín": {
        "coords": (40.4600, -3.6900),
        "weight": 1.00,
    },
    "Retiro": {
        "coords": (40.4153, -3.6844),
        "weight": 0.85,
    },
    "Latina": {
        "coords": (40.4000, -3.7500),
        "weight": 0.65,
    },
}


# --------------------------
# DEMANDA POR HORA
# --------------------------
def hour_weight(hour: int) -> float:
    if 9 <= hour <= 13 or 17 <= hour <= 19:
        return 1.0   # alta
    elif 8 <= hour < 9 or 16 <= hour < 17:
        return 0.6   # media
    elif 13 < hour < 16 or 19 < hour <= 20:
        return 0.3   # baja
    return 0.0


# --------------------------
# DEMANDA POR DÍA
# --------------------------
def day_weight(day_of_week: int) -> float:
    # 0=Lunes ... 4=Viernes
    if day_of_week == 0:
        return 1.25  # lunes alta
    elif day_of_week in [1, 2, 3]:
        return 1.0   # martes-jueves media
    elif day_of_week == 4:
        return 0.6   # viernes baja
    return 0.0       # fin de semana no se trabaja


# --------------------------
# SELECCIÓN DE ZONA CON PESOS
# --------------------------
def choose_zone() -> str:
    zone_names = list(ZONES.keys())
    weights = [ZONES[z]["weight"] for z in zone_names]
    return random.choices(zone_names, weights=weights, k=1)[0]


# --------------------------
# GENERAR COORDENADAS
# --------------------------
def generate_location(zone: str):
    center_lat, center_lon = ZONES[zone]["coords"]

    # Zonas con más demanda tienen puntos algo más concentrados
    zone_weight = ZONES[zone]["weight"]
    noise = 0.012 / zone_weight

    lat = center_lat + np.random.normal(0, noise)
    lon = center_lon + np.random.normal(0, noise)

    return lat, lon


# --------------------------
# GENERAR FECHA + HORA REALISTA
# --------------------------
def generate_datetime(zone: str):
    while True:
        day_offset = random.randint(0, 20)
        base_date = datetime.now() + timedelta(days=day_offset)
        day_of_week = base_date.weekday()

        if day_of_week > 4:
            continue

        hour = random.randint(8, 20)

        probability = (
            hour_weight(hour)
            * day_weight(day_of_week)
            * ZONES[zone]["weight"]
        )

        # Capar probabilidad para que no supere 1
        probability = min(probability, 0.95)

        if random.random() < probability:
            minute = random.choice([0, 15, 30, 45])

            appointment = base_date.replace(
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0
            )

            scheduled = appointment - timedelta(
                days=random.randint(1, 10),
                hours=random.randint(1, 48)
            )

            return scheduled, appointment


# --------------------------
# DURACIÓN SEGÚN SERVICIO
# --------------------------
def generate_service_duration() -> int:
    return random.choices(
        [30, 60, 90],
        weights=[0.25, 0.55, 0.20],
        k=1
    )[0]


# --------------------------
# NO-SHOW SEGÚN FRANJA
# --------------------------
def generate_no_show(appointment: datetime) -> int:
    hour = appointment.hour

    # Ligeramente más no-show en últimas horas
    if hour >= 18:
        p_no_show = 0.25
    elif 13 <= hour <= 16:
        p_no_show = 0.18
    else:
        p_no_show = 0.12

    return int(np.random.choice([0, 1], p=[1 - p_no_show, p_no_show]))


# --------------------------
# GENERAR DATASET
# --------------------------
def generate_dataset(n=NUM_SAMPLES):
    data = []

    for i in range(n):
        zone = choose_zone()

        lat, lon = generate_location(zone)
        scheduled, appointment = generate_datetime(zone)

        data.append({
            "appointment_id": i,
            "zone": zone,
            "latitude": lat,
            "longitude": lon,
            "scheduledday": scheduled,
            "appointmentday": appointment,
            "service_duration": generate_service_duration(),
            "no_show": generate_no_show(appointment),
        })

    return pd.DataFrame(data)


# --------------------------
# GUARDAR
# --------------------------
def save_dataset(df: pd.DataFrame):
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Dataset guardado en {OUTPUT_PATH}")


# --------------------------
# RESUMEN
# --------------------------
def print_summary(df: pd.DataFrame):
    df = df.copy()
    df["appointmentday"] = pd.to_datetime(df["appointmentday"])
    df["hour"] = df["appointmentday"].dt.hour
    df["day_of_week"] = df["appointmentday"].dt.dayofweek

    print("\nDistribución por zona:")
    print(df["zone"].value_counts())

    print("\nDistribución por hora:")
    print(df["hour"].value_counts().sort_index())

    print("\nDistribución por día de la semana:")
    print(df["day_of_week"].value_counts().sort_index())


# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    df = generate_dataset()
    save_dataset(df)

    print(df.head())
    print_summary(df)