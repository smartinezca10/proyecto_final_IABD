
from pathlib import Path

import pandas as pd
from pyspark.sql import DataFrame, SparkSession

from proyectoiabd.config.settings import settings


def load_raw_appointments_spark(
    spark: SparkSession,
    file_name: str = settings.RAW_APPOINTMENTS_FILE
) -> DataFrame:
    input_path = settings.RAW_DATA_PATH / file_name

    if not input_path.exists():
        raise FileNotFoundError(f"No existe el fichero: {input_path}")

    return spark.read.csv(
        str(input_path),
        header=True,
        inferSchema=True
    )


def save_processed_appointments(df: DataFrame) -> Path:
    """
    Spark procesa; Pandas escribe Parquet para evitar problemas Hadoop/Windows.
    """
    output_path = settings.PROCESSED_DATA_PATH / settings.PROCESSED_APPOINTMENTS_FILE
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pandas_df: pd.DataFrame = df.toPandas()
    pandas_df.to_parquet(output_path, index=False)
    
    print(f"Datos guardados en {output_path}")

    return output_path