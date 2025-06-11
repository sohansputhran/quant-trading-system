import requests, pandas as pd
from datetime import datetime

import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(".."))

# Import the API_KEY from your config module
from utils.config import NEWS_API_KEY

API_KEY = NEWS_API_KEY
# 100 is the maximum page size for NewsAPI
LIMIT = 100

FILENAME = f"catalyst_news_{datetime.now().strftime('%Y-%m-%d')}.csv"
FILE_PATH = os.path.join("../data/", FILENAME)

# --- Queries for different catalysts ---
QUERY_TOPICS = {
    "FDA_Approval": "FDA approval OR drug approval OR clinical trial results",
    "Earnings": "earnings beat OR earnings miss OR EPS beat OR quarterly results",
    "Mergers_Acquisitions": "acquires OR acquisition OR buyout OR merger announced",
    "Analyst_Upgrades": "analyst upgrade OR price target raised OR initiated coverage OR outperform",
    "Contracts": "awarded contract OR government deal OR defense contract OR signed deal",
    "Buybacks": "announces share buyback OR stock repurchase plan",
    "Executive_Changes": "CEO resigns OR new CEO OR insider buying OR director purchase",
    "AI_Tech": "AI breakthrough OR generative AI OR LLM launch OR quantum computing",
    "EV_Clean_Energy": "battery deal OR EV partnership OR solar expansion OR lithium mining",
    "Short_Squeeze": "short squeeze OR WallStreetBets OR trending stock OR high short interest"
}

# --- Fetch news for a given query ---
def fetch_news(query_label, query_text):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query_text,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": LIMIT,
        "apiKey": API_KEY
    }
    res = requests.get(url, params=params)
    if res.status_code != 200:
        print(f"Error fetching news for {query_label}: {res.status_code} - {res.text}")
        return []
    else:
        # print(f"Fetched {len(res.json().get('articles', []))} articles for {query_label}")
        
        # Extract articles from the response
        articles = res.json().get("articles", [])
        data = []

        for a in articles:
            title = a.get("title", "")
            desc = a.get("description", "")
            data.append({
                "topic": query_label,
                "publishedAt": a.get("publishedAt"),
                "source": a.get("source", {}).get("name", ""),
                "title": title,
                "description": desc,
                "url": a.get("url", "")
            })

        return data

def build_catalyst_news_list():
    all_articles = []
    for topic, query in QUERY_TOPICS.items():
        articles = fetch_news(topic, query, API_KEY)
        all_articles.extend(articles)
        
    df = pd.DataFrame(all_articles)
    
    # Append to existing file or create new one
    if os.path.exists(FILE_PATH):
        df_existing = pd.read_csv(FILE_PATH)
        df_combined = pd.concat([df_existing, df]).drop_duplicates()
        df_combined.to_csv(FILE_PATH, index=False)
        print(f"Appended to existing file: {FILE_PATH}")
    else:
        df.to_csv(FILE_PATH, index=False)
        print(f"Created new file: {FILE_PATH}")

if __name__ == "__main__":
    print("Starting catalyst news collection...")
    if not API_KEY:
        print("❌ NEWS_API_KEY is not set. Please check your config.")
        sys.exit(1)
    print(f"Using API_KEY: {API_KEY[:4]}... (truncated for security)")
    
    build_catalyst_news_list()
    print("Catalyst news collection completed.")