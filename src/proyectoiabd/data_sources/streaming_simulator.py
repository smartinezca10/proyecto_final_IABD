import time
import random
from datetime import datetime, timedelta

ZONES = ["Madrid Centro", "Salamanca", "Chamartín", "Retiro"]

def generate_random_appointment():
    return {
        "client_id": random.randint(1, 1000),
        "zone": random.choice(ZONES),
        "timestamp": datetime.now().isoformat(),
        "service_duration": random.choice([30, 60, 90])
    }


def stream_appointments(interval=2):
    while True:
        appointment = generate_random_appointment()
        print("New appointment request:", appointment)
        yield appointment
        time.sleep(interval)