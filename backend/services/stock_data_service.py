import yfinance as yf

def fetch_financial_metrics(symbol):
    try:
        # Finnhub symbol might be AAPL, but for Indian stocks it's RELIANCE.NS. 
        # yfinance uses Yahoo ticker format. We assume the symbol passed is valid.
        stock = yf.Ticker(symbol)
        
        # FALLBACK LOGIC: On cloud servers like Render, .info is often blocked/empty.
        # We fetch history to get the price reliably.
        try:
            hist = stock.history(period="1d")
        except:
            hist = None
            
        info = stock.info if stock.info else {}

        # If both are empty or unavailable, return None
        if (hist is None or hist.empty) and not info:
            return None

        # Prefer price from history for reliability on cloud
        if hist is not None and not hist.empty:
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Open'].iloc[-1] # Using daily open as baseline
        else:
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            prev_close = info.get('previousClose', 0)
        
        if current_price == 0:
            return None
        
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
