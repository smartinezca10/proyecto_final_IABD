import pandas as pd


def compute_cluster_centers(df: pd.DataFrame):
    return (
        df[df['cluster'] != -1]
        .groupby('cluster')[['latitude', 'longitude']]
        .mean()
        .reset_index()
    )


def compute_cluster_density(df: pd.DataFrame):
    return df.groupby('cluster').size().reset_index(name='count')