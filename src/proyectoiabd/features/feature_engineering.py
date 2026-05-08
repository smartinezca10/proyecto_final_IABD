from pyspark.sql import DataFrame
from pyspark.sql.functions import col, to_timestamp, hour, dayofweek, datediff


def add_time_features(df: DataFrame) -> DataFrame:
    df = df.withColumn(
        "scheduledday",
        to_timestamp(col("scheduledday"))
    )

    df = df.withColumn(
        "appointmentday",
        to_timestamp(col("appointmentday"))
    )

    df = df.withColumn(
        "hour",
        hour(col("appointmentday"))
    )

    df = df.withColumn(
        "day_of_week",
        dayofweek(col("appointmentday"))
    )

    df = df.withColumn(
        "waiting_days",
        datediff(col("appointmentday"), col("scheduledday"))
    )

    return df


def build_appointment_features(df: DataFrame) -> DataFrame:
    df = add_time_features(df)
    return df