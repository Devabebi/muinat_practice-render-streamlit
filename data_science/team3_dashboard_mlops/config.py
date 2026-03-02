import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CHURN_API_URL = os.getenv("CHURN_API_URL", "").strip()
    REC_API_URL = os.getenv("REC_API_URL", "").strip()

    MOCK_MODE = (
        (not CHURN_API_URL) or ("localhost" in CHURN_API_URL) or
        (not REC_API_URL)   or ("localhost" in REC_API_URL)
    )

settings = Settings()