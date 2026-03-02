from fastapi import FastAPI
from datetime import datetime, timezone
import hashlib

app = FastAPI()

def iso_utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def deterministic_float_0_1(key: str) -> float:
    """
    Convert a string key into a deterministic float in [0, 1].
    """
    h = hashlib.md5(key.encode("utf-8")).hexdigest()
    # take first 8 hex chars -> int -> scale to [0,1]
    value = int(h[:8], 16) / 0xFFFFFFFF
    return round(value, 2)

@app.get("/")
def home():
    return {"message": "Churn mock API running. Go to /docs"}

@app.post("/predict/churn")
def predict_churn(data: dict):
    customer_id = data.get("customer_id", "UNKNOWN")

    # deterministic churn probability based on customer_id
    churn_probability = deterministic_float_0_1(f"churn:{customer_id}")

    churn_prediction = "high_risk" if churn_probability >= 0.5 else "low_risk"

    # deterministic confidence (also based on customer_id)
    confidence = deterministic_float_0_1(f"conf:{customer_id}")
    # keep confidence within a nice range for demo (0.60–0.95)
    confidence = round(0.60 + (confidence * 0.35), 2)

    return {
        "customer_id": customer_id,
        "churn_probability": churn_probability,
        "churn_prediction": churn_prediction,
        "confidence": confidence,
        "model_version": "churn-model-v1.0",
        "timestamp": iso_utc_now(),
    }

print("API running!")
print("Swagger docs → http://127.0.0.1:8001/docs")