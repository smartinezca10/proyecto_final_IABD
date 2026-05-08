import pandas as pd
from sklearn.cluster import DBSCAN
import numpy as np


def run_dbscan(df: pd.DataFrame, eps_km=0.5, min_samples=5):
    """
    eps_km: radio en km para considerar vecinos
    """

    coords = df[['latitude', 'longitude']].values

    # Convertir km → radianes
    kms_per_radian = 6371.0088
    eps = eps_km / kms_per_radian

    db = DBSCAN(
        eps=eps,
        min_samples=min_samples,
        algorithm='ball_tree',
        metric='haversine'
    )

    clusters = db.fit_predict(np.radians(coords))

    df['cluster'] = clusters

    return df