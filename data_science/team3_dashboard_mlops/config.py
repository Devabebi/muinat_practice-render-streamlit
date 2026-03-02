import os
from dotenv import load_dotenv

# Load variables from the .env file (in your project root)
load_dotenv()

class Settings:
    # Default to mock localhost URLs if .env variables are missing
    CHURN_API_URL = os.getenv("CHURN_API_URL", "http://localhost:8001")
    REC_API_URL = os.getenv("REC_API_URL", "http://localhost:8012")

# Single shared settings object to import everywhere
settings = Settings()