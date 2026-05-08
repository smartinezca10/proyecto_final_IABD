import pandas as pd
import joblib
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


MODEL_PATH = "models/demand_model.pkl"


def build_demand_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte citas históricas en demanda agregada por zona, día y hora.
    Target: número de citas.
    """

    df = df.copy()

    df["appointmentday"] = pd.to_datetime(df["appointmentday"])

    df["date"] = df["appointmentday"].dt.date
    df["hour"] = df["appointmentday"].dt.hour
    df["day_of_week"] = df["appointmentday"].dt.dayofweek

    demand_df = (
        df.groupby(["zone", "date", "hour", "day_of_week"])
        .size()
        .reset_index(name="demand")
    )

    demand_df = pd.get_dummies(demand_df, columns=["zone"], drop_first=False)

    demand_df = demand_df.drop(columns=["date"])

    return demand_df


def train_demand_model(input_path="data/raw/appointments.csv"):
    df = pd.read_csv(input_path)

    demand_df = build_demand_dataset(df)

    X = demand_df.drop(columns=["demand"])
    y = demand_df["demand"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=8,
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)

    Path("models").mkdir(exist_ok=True)

    joblib.dump(
        {
            "model": model,
            "columns": X.columns.tolist(),
            "mae": mae
        },
        MODEL_PATH
    )

    print(f"Modelo guardado en {MODEL_PATH}")
    print(f"MAE: {mae:.2f} citas")


if __name__ == "__main__":
    train_demand_model()