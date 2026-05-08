from pydantic import BaseModel
from typing import List


class AppointmentRequest(BaseModel):
    latitude: float
    longitude: float
    zone: str | None = None
    hour: int = 10
    day_of_week: int = 2
    service_duration: int = 60


class PricingOption(BaseModel):
    price: float
    label: str
    delta_km: float
    delta_co2: float
    score: float
    hour: int
    day_of_week: int
    option_type: str
    predicted_demand: float = 0.0
    forced_green: bool = False
    zone: str | None = None
    explanation: str = ""


class PricingResponse(BaseModel):
    requested_option: PricingOption
    alternative_options: List[PricingOption]
    non_optimizable_zone: bool = False
    message: str | None = None