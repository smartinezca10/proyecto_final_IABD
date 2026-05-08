import pandas as pd
from pathlib import Path
from proyectoiabd.config.settings import settings

def load_appointments(file_name: str) -> pd.DataFrame:
    file_path = Path(settings.RAW_DATA_PATH) / file_name

    df = pd.read_csv(file_path)

    # Limpieza básica
    df = df.dropna()
    df.columns = df.columns.str.lower()

    return df


def preprocess_appointments(df: pd.DataFrame) -> pd.DataFrame:
    # Ejemplo: crear timestamp y features
    if 'scheduledday' in df.columns:
        df['scheduledday'] = pd.to_datetime(df['scheduledday'])

    if 'appointmentday' in df.columns:
        df['appointmentday'] = pd.to_datetime(df['appointmentday'])

    # Feature ejemplo
    df['waiting_days'] = (df['appointmentday'] - df['scheduledday']).dt.days

    return df