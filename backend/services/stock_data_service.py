import yfinance as yf

def fetch_financial_metrics(symbol):
    try:
        # Finnhub symbol might be AAPL, but for Indian stocks it's RELIANCE.NS. 
        # yfinance uses Yahoo ticker format. We assume the symbol passed is valid.
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Yahoo finance returns empty dict if the ticker is totally invalid
        if not info or 'regularMarketPrice' not in info and 'currentPrice' not in info and 'previousClose' not in info:
            return None

        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        prev_close = info.get('previousClose', 0)
        
        # Calculate percentage change
        change = current_price - prev_close
        percent_change = (change / prev_close * 100) if prev_close else 0

        # Format large numbers
        def format_large_number(num):
            if num is None: return "N/A"
            if num >= 1e12: return f"{num/1e12:.2f}T"
            if num >= 1e9: return f"{num/1e9:.2f}B"
            if num >= 1e6: return f"{num/1e6:.2f}M"
            return str(num)

        # Helper to format floats to 2 decimal places
        def f_2(num):
            return f"{num:.2f}" if isinstance(num, (int, float)) else 'N/A'

        return {
            "price": current_price,
            "change": change,
            "percent_change": percent_change,
            "open": f_2(info.get('open')),
            "high": f_2(info.get('dayHigh')),
            "low": f_2(info.get('dayLow')),
            "pe_ratio": f_2(info.get('trailingPE')),
            "market_cap": format_large_number(info.get('marketCap')),
            "avg_vol": format_large_number(info.get('averageVolume')),
            "52_high": f_2(info.get('fiftyTwoWeekHigh')),
            "52_low": f_2(info.get('fiftyTwoWeekLow')),
            "eps": f_2(info.get('trailingEps')),
            "dividend_yield": f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else 'N/A',
            "beta": f_2(info.get('beta')),
            "currency": info.get('financialCurrency', 'USD')
        }
    except Exception as e:
        print(f"Error fetching yfinance data: {e}")
        return None
