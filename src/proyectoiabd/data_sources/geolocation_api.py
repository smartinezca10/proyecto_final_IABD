import requests

def get_coordinates(address: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    
    return None, None


def get_distance_osrm(origin, destination):
    url = f"http://router.project-osrm.org/route/v1/driving/{origin[1]},{origin[0]};{destination[1]},{destination[0]}"
    
    response = requests.get(url)
    data = response.json()

    if "routes" in data:
        distance_m = data["routes"][0]["distance"]
        duration_s = data["routes"][0]["duration"]
        return distance_m / 1000, duration_s / 60  # km, minutos

    return None, None


def get_zone_from_coordinates(latitude: float, longitude: float) -> str:
    """
    Obtiene una zona/barrio aproximado usando OpenStreetMap Nominatim.
    """

    url = "https://nominatim.openstreetmap.org/reverse"

    params = {
        "lat": latitude,
        "lon": longitude,
        "format": "json",
        "addressdetails": 1,
        "zoom": 14,
    }

    headers = {
        "User-Agent": "EcoSchedulingOptimizer/1.0"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()
    address = data.get("address", {})

    zone = (
        address.get("city_district")
        or address.get("district")
        or address.get("borough")
        or address.get("suburb")
        or address.get("neighbourhood")
        or address.get("quarter")
        or address.get("city")
        or "Zona desconocida"
    )

    return zone