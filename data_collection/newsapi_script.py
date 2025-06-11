import requests, pandas as pd, re
from datetime import datetime, timedelta

import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(".."))

# Import the API_KEY from your config module
from utils.config import NEWS_API_KEY

API_KEY = NEWS_API_KEY
QUERY = "FDA OR earnings OR acquisition OR upgrade OR contract"
LIMIT = 50
date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
def get_general_news():
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": QUERY,
        "from": date_str, # datetime.now().strftime('%Y-%m-%d'),
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

def extract_tickers(text):
    return re.findall(r'\b[A-Z]{2,5}\b', text)

def build_catalyst_news_list():
    articles = get_general_news()
    rows = []
    for a in articles:
        title, desc = a.get("title",""), a.get("description","")
        tickers = set(extract_tickers(title + " " + desc))
        rows.append({
            "publishedAt": a.get("publishedAt"),
            "source": a.get("source",{}).get("name"),
            "title": title,
            "description": desc,
            "url": a.get("url"),
            "tickers": ", ".join(tickers)
        })
    df = pd.DataFrame(rows)
    out = f"catalyst_news_{datetime.now().strftime('%Y-%m-%d')}.csv"
    df.to_csv(out, index=False)
    print("Saved:", out)