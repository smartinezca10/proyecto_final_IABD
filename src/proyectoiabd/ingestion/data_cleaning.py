from pyspark.sql import DataFrame
from pyspark.sql.functions import col


def normalize_column_names(df: DataFrame) -> DataFrame:
    for column in df.columns:
        df = df.withColumnRenamed(column, column.strip().lower())

    return df


def remove_null_rows(df: DataFrame) -> DataFrame:
    return df.dropna()


def filter_valid_coordinates(df: DataFrame) -> DataFrame:
    if "latitude" not in df.columns or "longitude" not in df.columns:
        return df

    return df.filter(
        (col("latitude").isNotNull()) &
        (col("longitude").isNotNull())
    )


def clean_appointments(df: DataFrame) -> DataFrame:
    df = normalize_column_names(df)
    df = remove_null_rows(df)
    df = filter_valid_coordinates(df)

    return df