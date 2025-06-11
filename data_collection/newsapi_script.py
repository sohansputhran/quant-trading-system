import requests, pandas as pd, re, pytz
from datetime import datetime, timedelta

import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(".."))

# Import the API_KEY from your config module
from utils.config import NEWS_API_KEY

API_KEY = NEWS_API_KEY
QUERY = "FDA OR earnings OR acquisition OR upgrade OR contract"
# 100 is the maximum page size for NewsAPI
LIMIT = 100
# date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

FILENAME = f"catalyst_news_{datetime.now().strftime('%Y-%m-%d')}.csv"
FILE_PATH = os.path.join("../data/", FILENAME)

# Function to get the current time in Zulu (UTC) ISO 8601 format for the newsapi query
# def get_current_zulu_time():
#     """Returns the current time in Zulu (UTC) ISO 8601 format."""
#     utc_now = datetime.now(pytz.utc)
#     return utc_now.strftime('%Y-%m-%dT%H:%M:%SZ')

def get_general_news():
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": QUERY,
        # "from": get_current_zulu_time(),
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": LIMIT,
        "apiKey": API_KEY
    }
    response = requests.get(url, params=params)
    # print("Status:", response.status_code)
    # print("Response:", response.json())
    if response.status_code != 200:
        print("Error fetching news:", response.status_code, response.text)
        return []
    else:
        return response.json().get("articles", [])

def build_catalyst_news_list():
    articles = get_general_news()
    rows = []
    for a in articles:
        title, desc = a.get("title",""), a.get("description","")

        rows.append({
            "publishedAt": a.get("publishedAt"),
            "source": a.get("source",{}).get("name"),
            "title": title,
            "description": desc,
            "url": a.get("url")
        })
    df = pd.DataFrame(rows)
    
    # Append to existing file or create new one
    if os.path.exists(FILE_PATH):
        df_existing = pd.read_csv(FILE_PATH)
        df_combined = pd.concat([df_existing, df]).drop_duplicates()
        df_combined.to_csv(FILE_PATH, index=False)
        print(f"Appended to existing file: {FILE_PATH}")
    else:
        df.to_csv(FILE_PATH, index=False)
        print(f"Created new file: {FILE_PATH}")