def compute_green_score(delta_km, delta_co2, cluster_density):

    # pesos ajustables
    w_km = 0.5
    w_co2 = 0.3
    w_cluster = 0.2

    # Normalización simple
    score = (
        -w_km * delta_km +       # menos km = mejor
        -w_co2 * delta_co2 +     # menos CO2 = mejor
        w_cluster * cluster_density
    )

    return score