from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv

# Load nearest .env (works no matter your CWD)
load_dotenv(find_dotenv(usecwd=True))

FRED_API_KEY = os.getenv("FRED_API_KEY")  # required for FRED
