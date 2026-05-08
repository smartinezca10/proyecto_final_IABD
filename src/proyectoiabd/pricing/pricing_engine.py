import pandas as pd

from proyectoiabd.pricing.green_score import compute_green_score
from proyectoiabd.demand.demand_predictor import predict_demand
from proyectoiabd.routing.distance_matrix import build_distance_matrix
from proyectoiabd.routing.vrp_solver import solve_vrp
from proyectoiabd.routing.route_analysis import compute_route_distance, compute_route_co2




BASE_PRICE = 50


def evaluate_appointment(current_df: pd.DataFrame, new_appointment: dict):

    zone = new_appointment.get("zone", "Centro")
    hour = new_appointment.get("hour", 10)
    day_of_week = new_appointment.get("day_of_week", 2)

    predicted_demand = predict_demand(zone, hour, day_of_week)
    
    # -----------------------
    # 1. Ruta actual
    # -----------------------
    current_matrix = build_distance_matrix(current_df)
    current_route = solve_vrp(current_matrix)[0]

    current_distance = compute_route_distance(current_route, current_matrix)
    current_co2 = compute_route_co2(current_route, current_matrix)

    # -----------------------
    # 2. Añadir nueva cita
    # -----------------------
    new_df = pd.concat([
        current_df,
        pd.DataFrame([new_appointment])
    ], ignore_index=True)

    new_matrix = build_distance_matrix(new_df)
    new_route = solve_vrp(new_matrix)[0]

    new_distance = compute_route_distance(new_route, new_matrix)
    new_co2 = compute_route_co2(new_route, new_matrix)

    # -----------------------
    # 3. Impacto
    # -----------------------
    delta_km = new_distance - current_distance
    delta_co2 = new_co2 - current_co2

    # cluster density
    cluster_density = len(current_df) + predicted_demand

    # -----------------------
    # 4. Green Score
    # -----------------------
    score = compute_green_score(delta_km, delta_co2, cluster_density)

    # -----------------------
    # 5. Pricing
    # -----------------------
    if score > 5:
        price = BASE_PRICE * 0.8
        label = "🌱 GREEN SLOT"
    elif score > 0:
        price = BASE_PRICE * 0.95
        label = "🟢 LIGHT GREEN"
    else:
        price = BASE_PRICE * (1 + abs(delta_km) * 0.05)
        label = "🔴 HIGH IMPACT"

    return {
        "price": round(price, 2),
        "label": label,
        "delta_km": round(delta_km, 2),
        "delta_co2": round(delta_co2, 2),
        "score": round(score, 2)
    }