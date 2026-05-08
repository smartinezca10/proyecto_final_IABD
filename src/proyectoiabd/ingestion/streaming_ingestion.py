from pyspark.sql import SparkSession


def create_streaming_df():
    spark = SparkSession.builder.getOrCreate()

    # Simulación simple con rate source
    df = spark.readStream.format("rate").option("rowsPerSecond", 1).load()

    return df