from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env file

# Global configuration variables

INTRADAY_DAYS_LIMIT = 59
API_KEY = os.getenv("ALPHA_API_KEY")
DEFAULT_CURRENCY = "USD"
DEFAULT_INTERVAL = "5m"


