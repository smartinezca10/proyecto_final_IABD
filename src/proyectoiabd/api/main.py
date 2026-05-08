from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from proyectoiabd.api.schemas import AppointmentRequest, PricingResponse
from proyectoiabd.api.services import calculate_dynamic_price_with_alternatives


app = FastAPI(
    title="Eco-Scheduling Optimizer API",
    description="Backend para pricing dinámico, rutas y métricas ESG",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "Eco-Scheduling Optimizer API"
    }

@app.post("/pricing/evaluate", response_model=PricingResponse)
def evaluate_pricing(request: AppointmentRequest):
    print(f"Evaluando cita: {request}")
    result = calculate_dynamic_price_with_alternatives(request.model_dump())
    print(f"Resultado: {result}")
    return result