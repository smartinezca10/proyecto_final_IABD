import pandas as pd
from pathlib import Path

from proyectoiabd.pricing.pricing_engine import evaluate_appointment
from proyectoiabd.data_sources.geolocation_api import get_zone_from_coordinates

try:
    from proyectoiabd.demand.demand_predictor import predict_demand
except Exception:
    predict_demand = None


DATA_PATH = Path("data/processed/appointments_features.parquet")


DAY_NAMES = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo",
}


# ==========================================================
# CARGA DE DATOS
# ==========================================================
def load_full_dataset() -> pd.DataFrame:
    df = pd.read_parquet(DATA_PATH)

    required_columns = ["latitude", "longitude", "day_of_week", "hour"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Falta la columna obligatoria: {col}")

    return df


# ==========================================================
# PREDICCIÓN DE DEMANDA
# ==========================================================
def get_predicted_demand(zone: str, hour: int, day_of_week: int) -> float:
    """
    Si existe modelo predictivo entrenado, lo usa.
    Si no existe o falla, devuelve 0 para no romper la API.
    """
    if predict_demand is None:
        return 0.0

    try:
        print(f"Prediciendo demanda para zona={zone}, hora={hour}, día={day_of_week}")
        result = float(
            predict_demand(
                zone=zone,
                hour=hour,
                day_of_week=day_of_week,
            )
        )
        print(f"Resultado de predict_demand: {result}")
        return result

    except Exception as exc:
        print(
            f"Error al predecir demanda para zona={zone}, "
            f"hora={hour}, día={day_of_week}: {exc}"
        )
        return 0.0


# ==========================================================
# AGENDA POR SLOT
# ==========================================================
def load_schedule_for_slot(day_of_week: int, hour: int) -> pd.DataFrame:
    """
    Devuelve las citas existentes para una franja concreta.
    Si hay pocos datos, amplía la ventana temporal.
    Si aun así hay pocos datos, usa una muestra aleatoria.
    """
    df = load_full_dataset()

    slot_df = df[
        (df["day_of_week"] == day_of_week)
        & (df["hour"] == hour)
    ].copy()

    if len(slot_df) < 5:
        slot_df = df[
            (df["day_of_week"] == day_of_week)
            & (df["hour"].between(hour - 1, hour + 1))
        ].copy()

    if len(slot_df) < 5:
        slot_df = df.sample(min(12, len(df)), random_state=42)

    return slot_df.head(12).reset_index(drop=True)


# ==========================================================
# EXPLICACIÓN COMERCIAL
# ==========================================================
def build_explanation(option: dict, requested_price: float | None = None) -> str:
    day = DAY_NAMES.get(option["day_of_week"], f"Día {option['day_of_week']}")
    hour = option["hour"]
    demand = option.get("predicted_demand", 0)

    if "GREEN" in option["label"].upper():
        reason = (
            "Este horario encaja mejor con citas ya agrupadas en la zona, "
            "reduciendo desplazamientos y emisiones."
        )
    elif option["delta_km"] <= 0:
        reason = (
            "Este horario mejora la ruta actual y reduce kilómetros respecto "
            "a una cita aislada."
        )
    else:
        reason = (
            "Este horario tiene menor eficiencia logística, por lo que no recibe "
            "el máximo incentivo verde."
        )

    saving_text = ""

    if requested_price is not None:
        saving = round(requested_price - option["price"], 2)

        if saving > 0:
            saving_text = (
                f" Supone un ahorro estimado de {saving} € "
                "frente a la opción solicitada."
            )

    demand_text = ""

    if demand > 0:
        demand_text = f" La demanda prevista para este slot es de {demand:.2f} citas."

    return f"{day} a las {hour}:00. {reason}{saving_text}{demand_text}"


# ==========================================================
# REGLAS DE EVALUACIÓN
# ==========================================================
def is_green_option(option: dict) -> bool:
    """
    Determina si una opción puede considerarse verde.
    Se usa para aplicar un pequeño incentivo por demanda solo si
    la opción ya tiene sentido logístico/ambiental.
    """
    return (
        "GREEN" in option["label"].upper()
        or option["score"] > 0
        or option["delta_km"] <= 0
        or option["delta_co2"] <= 0
    )


def is_meaningful_alternative(
    option: dict,
    requested_option: dict,
    min_price_saving: float = 3.0,
    min_km_improvement: float = 0.3,
    min_co2_improvement: float = 0.03,
) -> bool:
    """
    Una alternativa se recomienda si mejora el precio o el impacto logístico/ambiental.

    En zonas no optimizables puede mostrarse una alternativa comercial más barata,
    aunque no represente una cita verde.
    """
    price_saving = requested_option["price"] - option["price"]
    km_improvement = requested_option["delta_km"] - option["delta_km"]
    co2_improvement = requested_option["delta_co2"] - option["delta_co2"]

    improves_price = price_saving >= min_price_saving

    improves_environment = (
        km_improvement >= min_km_improvement
        or co2_improvement >= min_co2_improvement
    )

    return improves_price or improves_environment


def deduplicate_options(options: list[dict]) -> list[dict]:
    """
    Evita mostrar alternativas prácticamente iguales.
    """
    unique_options = []
    seen = set()

    for opt in options:
        key = (
            opt["day_of_week"],
            opt["hour"],
            round(opt["price"], 2),
            round(opt["delta_km"], 2),
            round(opt["delta_co2"], 2),
        )

        if key not in seen:
            seen.add(key)
            unique_options.append(opt)

    return unique_options


def is_non_optimizable_zone(
    requested_option: dict,
    alternative_options: list[dict],
    min_km_threshold: float = 25.0,
    min_co2_threshold: float = 3.0,
) -> bool:
    high_impact = (
        requested_option["delta_km"] >= min_km_threshold
        or requested_option["delta_co2"] >= min_co2_threshold
    )

    has_green_alternative = any(is_green_option(opt) for opt in alternative_options)

    return high_impact and not has_green_alternative

# ==========================================================
# CÁLCULO PRINCIPAL
# ==========================================================
def calculate_dynamic_price_with_alternatives(appointment: dict) -> dict:

    # -------------------------
    # ZONA AUTOMÁTICA
    # -------------------------
    zone = appointment.get("zone")

    if not zone:
        zone = get_zone_from_coordinates(
            appointment["latitude"],
            appointment["longitude"],
        )

    appointment["zone"] = zone

    # -------------------------
    # OPCIÓN SOLICITADA
    # -------------------------
    requested_schedule = load_schedule_for_slot(
        appointment["day_of_week"],
        appointment["hour"],
    )

    requested_result = evaluate_appointment(
        current_df=requested_schedule,
        new_appointment=appointment,
    )

    requested_demand = get_predicted_demand(
        zone=zone,
        hour=appointment["hour"],
        day_of_week=appointment["day_of_week"],
    )

    requested_option = {
        **requested_result,
        "hour": appointment["hour"],
        "day_of_week": appointment["day_of_week"],
        "option_type": "requested",
        "predicted_demand": requested_demand,
        "zone": zone,
        "forced_green": False,
    }

    requested_option["explanation"] = build_explanation(requested_option)

    # -------------------------
    # CANDIDATOS ALTERNATIVOS
    # -------------------------
    candidate_slots = []

    for day_offset in [-3, -2, -1, 0, 1, 2, 3]:
        for hour_offset in [-4, -3, -2, -1, 1, 2, 3, 4]:

            candidate_day = (appointment["day_of_week"] + day_offset) % 7
            # Solo lunes-viernes
            if candidate_day > 4:
                continue
            
            candidate_hour = appointment["hour"] + hour_offset
            # Solo horas laborales
            if candidate_hour < 8 or candidate_hour > 20:
                continue

            if (
                candidate_day == appointment["day_of_week"]
                and candidate_hour == appointment["hour"]
            ):
                continue

            candidate_appointment = {
                **appointment,
                "day_of_week": candidate_day,
                "hour": candidate_hour,
            }

            candidate_schedule = load_schedule_for_slot(
                candidate_day,
                candidate_hour,
            )

            result = evaluate_appointment(
                current_df=candidate_schedule,
                new_appointment=candidate_appointment,
            )

            predicted_demand = get_predicted_demand(
                zone=zone,
                hour=candidate_hour,
                day_of_week=candidate_day,
            )

            option = {
                **result,
                "hour": candidate_hour,
                "day_of_week": candidate_day,
                "option_type": "alternative",
                "predicted_demand": predicted_demand,
                "zone": zone,
                "forced_green": False,
            }

            # Bonus suave por demanda prevista:
            # Solo se aplica si la opción ya es verde o eficiente.
            if is_green_option(option) and predicted_demand >= 2:
                option["price"] = round(option["price"] * 0.97, 2)

            candidate_slots.append(option)

    # -------------------------
    # FILTRAR ALTERNATIVAS REALMENTE MEJORES
    # -------------------------
    meaningful_candidates = [
        opt
        for opt in candidate_slots
        if is_meaningful_alternative(opt, requested_option)
    ]

    unique_candidates = deduplicate_options(meaningful_candidates)

    alternative_options = sorted(
        unique_candidates,
        key=lambda x: (x["price"], x["delta_km"], x["delta_co2"]),
    )[:2]

    # -------------------------
    # EXPLICACIONES DE ALTERNATIVAS
    # -------------------------
    for option in alternative_options:
        option["explanation"] = build_explanation(
            option,
            requested_price=requested_option["price"],
        )

    non_optimizable_zone = is_non_optimizable_zone(
        requested_option,
        alternative_options,
    )

    message = None

    if non_optimizable_zone:
        message = (
            "No hay agrupación posible en tu zona porque se encuentra lejos "
            "de las áreas habituales de servicio. Las alternativas mostradas "
            "pueden mejorar el precio por disponibilidad o demanda, pero no "
            "representan una cita verde."
        )

    return {
        "requested_option": requested_option,
        "alternative_options": alternative_options,
        "non_optimizable_zone": non_optimizable_zone,
        "message": message,
    }