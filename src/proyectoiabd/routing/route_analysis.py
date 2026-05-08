from proyectoiabd.data_sources.emissions_api import estimate_co2


def compute_route_distance(route, distance_matrix):
    total = 0

    for i in range(len(route) - 1):
        total += distance_matrix[route[i]][route[i+1]]

    return total


def compute_route_co2(route, distance_matrix):
    distance = compute_route_distance(route, distance_matrix)
    return estimate_co2(distance)