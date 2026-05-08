EMISSION_FACTOR_KG_PER_KM = 0.12  # 120g/km típico

def estimate_co2(distance_km: float) -> float:
    """
    Devuelve kg de CO2
    """
    return distance_km * EMISSION_FACTOR_KG_PER_KM


def estimate_fuel_savings(distance_km: float, fuel_per_100km=8):
    """
    litros ahorrados
    """
    return (distance_km * fuel_per_100km) / 100