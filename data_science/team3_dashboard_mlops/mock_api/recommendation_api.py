from fastapi import FastAPI, Query, HTTPException
from datetime import datetime, timezone
import hashlib
import re

app = FastAPI()

# ✅ accept IDs like CUST000001, CUST000009, CUST123456 etc.
CUST_PATTERN = re.compile(r"^CUST\d{6,}$")  # 6+ digits, adjust if needed

PRODUCTS = [
    {"product_id": "PROD00001", "product_name": "Cultural Home", "category": "Home"},
    {"product_id": "PROD00002", "product_name": "Premium Coffee Beans", "category": "Grocery"},
    {"product_id": "PROD00003", "product_name": "Wireless Earbuds", "category": "Electronics"},
    {"product_id": "PROD00004", "product_name": "Running Shoes", "category": "Sports"},
    {"product_id": "PROD00005", "product_name": "Yoga Mat", "category": "Sports"},
    {"product_id": "PROD00006", "product_name": "Face Cream", "category": "Beauty"},
    {"product_id": "PROD00007", "product_name": "Kitchen Blender", "category": "Home"},
]

def iso_utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def deterministic_score(customer_id: str, product_id: str) -> float:
    key = f"rec:{customer_id}:{product_id}"
    h = hashlib.md5(key.encode("utf-8")).hexdigest()
    value = int(h[:8], 16) / 0xFFFFFFFF
    score = 0.50 + (value * 0.49)  # 0.50–0.99
    return round(score, 2)

def validate_customer_id(customer_id: str):
    # ✅ UNKNOWN, abc, empty, etc should still return 404
    if not CUST_PATTERN.match(customer_id):
        raise HTTPException(status_code=404, detail="customer_id not found")

@app.get("/")
def home():
    return {"message": "Recommendation mock API running. Go to /docs"}

@app.get("/recommend/{customer_id}")
def recommend(customer_id: str, n: int = Query(5, ge=1, le=20)):
    customer_id = customer_id.strip().upper()
    validate_customer_id(customer_id)

    recs = []
    for p in PRODUCTS:
        recs.append({
            "product_id": p["product_id"],
            "product_name": p["product_name"],
            "category": p["category"],
            "predicted_score": deterministic_score(customer_id, p["product_id"])
        })

    # contract: sort descending by predicted_score
    recs = sorted(recs, key=lambda x: x["predicted_score"], reverse=True)

    return {
        "customer_id": customer_id,
        "recommendations": recs[:min(n, len(recs))],
        "model_version": "rec-model-v1.0",
        "timestamp": iso_utc_now()
    }

print("API running!")
print("Swagger docs → http://127.0.0.1:8012/docs")