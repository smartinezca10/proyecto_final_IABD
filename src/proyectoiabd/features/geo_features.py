from pyspark.sql.functions import udf, lit
from pyspark.sql.types import DoubleType
import math

# Distancia Haversine
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi/2)**2 +
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    )

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))


haversine_udf = udf(haversine, DoubleType())


def add_distance_feature(df, ref_lat, ref_lon):
    return df.withColumn(
        "distance_from_center",
        haversine_udf(
            df["latitude"],
            df["longitude"],
            lit(ref_lat),
            lit(ref_lon)
        )
    )