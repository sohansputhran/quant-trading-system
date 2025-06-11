import requests
import json
import pandas as pd

# URLs for exchange symbol lists
url_nasdaq = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/nasdaq/nasdaq_tickers.json"
url_nyse   = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/nyse/nyse_tickers.json"
# url_amex   = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/amex/amex_tickers.json"

def load_symbols(url):
    return json.loads(requests.get(url).text)

# Combine ticker symbols
tickers = set(load_symbols(url_nasdaq) + load_symbols(url_nyse)) # + load_symbols(url_amex))

# Save to CSV
df = pd.DataFrame({"symbol": sorted(tickers)})
df.to_csv("../data/tickers.csv", index=False)
print(f"✅ Saved {len(tickers)} unique tickers to data/tickers.csv")
