from pathlib import Path

from proyectoiabd.ingestion.batch_ingestion import (
    load_raw_appointments_spark,
    save_processed_appointments,
)
from proyectoiabd.ingestion.data_cleaning import clean_appointments
from proyectoiabd.features.feature_engineering import build_appointment_features
from proyectoiabd.utils.spark_session import create_spark_session, stop_spark_session


def run_appointments_pipeline() -> Path:
    spark = None

    try:
        spark = create_spark_session()

        raw_df = load_raw_appointments_spark(spark)
        clean_df = clean_appointments(raw_df)
        features_df = build_appointment_features(clean_df)

        output_path = save_processed_appointments(features_df)

        print("✅ Pipeline completado")
        print(f"📦 Dataset procesado guardado en: {output_path}")

        return output_path

    finally:
        print("🛑 Cerrando SparkSession...")
        stop_spark_session(spark)
        print("✅ SparkSession cerrada")