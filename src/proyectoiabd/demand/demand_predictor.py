import pandas as pd
import joblib

MODEL_PATH = "models/demand_model.pkl"


def load_demand_model():
    return joblib.load(MODEL_PATH)


def predict_demand(zone: str, hour: int, day_of_week: int) -> float:
    """
    Predice demanda esperada para una zona, hora y día de la semana.
    day_of_week: lunes=0, domingo=6
    """

    bundle = load_demand_model()

    model = bundle["model"]
    columns = bundle["columns"]

    row = pd.DataFrame([{
        "hour": hour,
        "day_of_week": day_of_week,
        f"zone_{zone}": 1
    }])

    for col in columns:
        if col not in row.columns:
            row[col] = 0

    row = row[columns]

    prediction = model.predict(row)[0]

    return round(float(prediction), 2)


if __name__ == "__main__":
    result = predict_demand(
        zone="Centro",
        hour=10,
        day_of_week=2
    )

    print(f"Demanda estimada: {result} citas")