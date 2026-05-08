from pyspark.sql import SparkSession

from proyectoiabd.config.settings import settings


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName(settings.SPARK_APP_NAME)
        .master(settings.SPARK_MASTER)
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )


def stop_spark_session(spark: SparkSession) -> None:
    if spark is not None:
        try:
            spark.stop()
            print("✅ Spark detenido correctamente")
        except Exception as e:
            print(f"⚠️ Error cerrando Spark: {e}")