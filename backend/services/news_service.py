import yfinance as yf
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FINNHUB_API_KEY")

def fetch_news(symbol):
    """
    Fetch news using yfinance as a reliable alternative to Finnhub.
    """
    try:
        stock = yf.Ticker(symbol)
        yf_news = stock.news
        
        if not yf_news:
            print(f"DEBUG: No news found for {symbol} via yfinance")
            return []

        articles = []
        # Take up to 8 articles for better distribution
        for item in yf_news[:8]:
            # Handle both old and new yfinance news formats
            content = item.get("content", item)
            
            # Extract URL from nested dictionaries if necessary
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
        print(f"DEBUG: News Error (yfinance): {e}")
        return []

def get_stock_symbol(stock_name):
    """
    Still use Finnhub for symbol search as it handles company names better than yfinance.
    """
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
                
                if symbol == query_upper:
                    score += 100
                
                base_symbol = symbol.split(".")[0] if "." in symbol else symbol
                if base_symbol == query_upper:
                    score += 50
                    
                desc_words = desc.split()
                if query_upper in desc_words:
                    score += 40
                elif query_upper in desc:
                    score += 10
                    
                if "." not in symbol:
                    score += 5
                elif symbol.endswith(".NS") or symbol.endswith(".BO"):
                    score += 4
                
                return score

            results_sorted = sorted(results, key=score_result, reverse=True)
            best_result = results_sorted[0]
            
            return best_result["symbol"], best_result["description"]
    except Exception as e:
        print(f"DEBUG: Symbol Search Error: {e}")
    
    return None, None