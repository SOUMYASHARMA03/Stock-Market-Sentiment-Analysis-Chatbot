import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from services.news_service import get_stock_symbol
from services.stock_data_service import fetch_financial_metrics

def test_stock(name):
    print(f"Testing search for: {name}")
    symbol, desc = get_stock_symbol(name)
    print(f"Resolved Symbol: {symbol}")
    print(f"Description: {desc}")
    
    if symbol:
        print(f"Fetching metrics for {symbol}...")
        metrics = fetch_financial_metrics(symbol)
        if metrics:
            print("SUCCESS: Metrics fetched!")
            print(f"Price: {metrics['price']}")
        else:
            print("FAILED: Could not fetch metrics.")
    else:
        print("FAILED: Could not resolve symbol.")

if __name__ == "__main__":
    test_stock("TESLA")
    print("-" * 20)
    test_stock("TATA")
