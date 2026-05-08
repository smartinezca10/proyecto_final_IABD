
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:

    # Claves API para conectar el en futuro con servicios externos (Google Maps, Carbon API, etc.)
    #GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    #CARBON_API_KEY = os.getenv("CARBON_API_KEY")

    PROJECT_ROOT = Path(__file__).resolve().parents[3]

    DATA_DIR = PROJECT_ROOT / "data"
    RAW_DATA_PATH = DATA_DIR / "raw"
    PROCESSED_DATA_PATH = DATA_DIR / "processed"

    RAW_APPOINTMENTS_FILE = "appointments.csv"
    PROCESSED_APPOINTMENTS_FILE = "appointments_features.parquet"

    SPARK_APP_NAME = "EcoSchedulingOptimizer"
    SPARK_MASTER = "local[*]"


settings = Settings()