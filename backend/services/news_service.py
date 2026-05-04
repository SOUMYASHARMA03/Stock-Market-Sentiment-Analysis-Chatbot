import yfinance as yf
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FINNHUB_API_KEY")

MOCK_NEWS = {
    "AAPL": [
        {"title": "Apple Intelligence features expected to boost iPhone 16 sales", "url": "https://finance.yahoo.com/quote/AAPL"},
        {"title": "Analysts upgrade Apple price target citing services growth", "url": "https://finance.yahoo.com/quote/AAPL"},
        {"title": "Apple becomes first company to hit $3 trillion market cap", "url": "https://finance.yahoo.com/quote/AAPL"}
    ],
    "APPLE": [
        {"title": "Apple Intelligence features expected to boost iPhone 16 sales", "url": "https://finance.yahoo.com/quote/AAPL"},
        {"title": "Analysts upgrade Apple price target citing services growth", "url": "https://finance.yahoo.com/quote/AAPL"},
        {"title": "Apple becomes first company to hit $3 trillion market cap", "url": "https://finance.yahoo.com/quote/AAPL"}
    ],
    "TSLA": [
        {"title": "Tesla Cybercab event reveals vision for autonomous future", "url": "https://finance.yahoo.com/quote/TSLA"},
        {"title": "Elon Musk announces new Gigafactory expansion plans", "url": "https://finance.yahoo.com/quote/TSLA"},
        {"title": "Tesla quarterly deliveries beat analyst expectations", "url": "https://finance.yahoo.com/quote/TSLA"}
    ],
    "TESLA": [
        {"title": "Tesla Cybercab event reveals vision for autonomous future", "url": "https://finance.yahoo.com/quote/TSLA"},
        {"title": "Elon Musk announces new Gigafactory expansion plans", "url": "https://finance.yahoo.com/quote/TSLA"},
        {"title": "Tesla quarterly deliveries beat analyst expectations", "url": "https://finance.yahoo.com/quote/TSLA"}
    ],
    "RELIANCE": [
        {"title": "Reliance Industries expands green energy portfolio with new acquisition", "url": "https://finance.yahoo.com/quote/RELIANCE.NS"},
        {"title": "Jio Financial Services shares hit new 52-week high", "url": "https://finance.yahoo.com/quote/RELIANCE.NS"},
        {"title": "Reliance retail division records double digit growth", "url": "https://finance.yahoo.com/quote/RELIANCE.NS"}
    ],
    "RELIANCE.NS": [
        {"title": "Reliance Industries expands green energy portfolio with new acquisition", "url": "https://finance.yahoo.com/quote/RELIANCE.NS"},
        {"title": "Jio Financial Services shares hit new 52-week high", "url": "https://finance.yahoo.com/quote/RELIANCE.NS"},
        {"title": "Reliance retail division records double digit growth", "url": "https://finance.yahoo.com/quote/RELIANCE.NS"}
    ],
    "MSFT": [
        {"title": "Microsoft Cloud revenue surprises analysts with 23% growth", "url": "https://finance.yahoo.com/quote/MSFT"},
        {"title": "New Surface devices integrate specialized AI hardware", "url": "https://finance.yahoo.com/quote/MSFT"}
    ],
    "MICROSOFT": [
        {"title": "Microsoft Cloud revenue surprises analysts with 23% growth", "url": "https://finance.yahoo.com/quote/MSFT"},
        {"title": "New Surface devices integrate specialized AI hardware", "url": "https://finance.yahoo.com/quote/MSFT"}
    ],
    "MARUTI": [
        {"title": "Maruti Suzuki reports record monthly sales in passenger vehicle segment", "url": "https://finance.yahoo.com/quote/MARUTI.NS"},
        {"title": "Maruti to launch new hybrid SUV model by end of year", "url": "https://finance.yahoo.com/quote/MARUTI.NS"}
    ],
    "MARUTI.NS": [
        {"title": "Maruti Suzuki reports record monthly sales in passenger vehicle segment", "url": "https://finance.yahoo.com/quote/MARUTI.NS"},
        {"title": "Maruti to launch new hybrid SUV model by end of year", "url": "https://finance.yahoo.com/quote/MARUTI.NS"}
    ]
}

def fetch_news(symbol):
    try:
        # Standard Fetch WITHOUT custom session (to avoid Render crashes)
        stock = yf.Ticker(symbol)
        yf_news = []
        try:
            yf_news = stock.news
        except:
            pass
        
        if not yf_news:
            print(f"DEBUG: yfinance news blocked. Checking Mock News for {symbol}")
            clean_symbol = symbol.upper().split('.')[0]
            return MOCK_NEWS.get(clean_symbol, MOCK_NEWS.get(symbol.upper(), []))

        articles = []
        for item in yf_news[:8]:
            content = item.get("content", item)
            raw_url = content.get("canonicalUrl", content.get("clickThroughUrl", content.get("link", "#")))
            if isinstance(raw_url, dict):
                url = raw_url.get("url", "#")
            else:
                url = raw_url

            articles.append({
                "title": content.get("title", "No Title"),
                "url": url
            })

        return articles
    except Exception as e:
        print(f"DEBUG: News Error: {e}")
        clean_symbol = symbol.upper().split('.')[0]
        return MOCK_NEWS.get(clean_symbol, MOCK_NEWS.get(symbol.upper(), []))

def get_stock_symbol(stock_name):
    try:
        url = f"https://finnhub.io/api/v1/search?q={stock_name}&token={API_KEY}"
        data = requests.get(url).json()
        if data.get("count", 0) == 0 and " " in stock_name:
            return get_stock_symbol(stock_name.split()[0])
        if data.get("count", 0) > 0:
            results = data["result"]
            query_upper = stock_name.upper()
            def score_result(res):
                symbol = res.get("symbol", "").upper()
                desc = res.get("description", "").upper()
                score = 0
                if symbol == query_upper: score += 100
                base_symbol = symbol.split(".")[0] if "." in symbol else symbol
                if base_symbol == query_upper: score += 50
                desc_words = desc.split()
                if query_upper in desc_words: score += 40
                elif query_upper in desc: score += 10
                if "." not in symbol: score += 5
                elif symbol.endswith(".NS") or symbol.endswith(".BO"): score += 4
                return score
            results_sorted = sorted(results, key=score_result, reverse=True)
            best_result = results_sorted[0]
            return best_result["symbol"], best_result["description"]
    except Exception as e:
        print(f"DEBUG: Symbol Search Error: {e}")
    return None, None