from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.news_service import fetch_news, get_stock_symbol
from services.sentiment_service import analyze_sentiment
from services.social_service import fetch_social_sentiment
from services.ai_service import chatbot
import statistics
from services.stock_data_service import fetch_financial_metrics
import yfinance as yf
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Point to the frontend folder
backend_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.abspath(os.path.join(backend_dir, "..", "frontend"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/analyze/{stock}")
def analyze_stock(stock: str):
    try:
        symbol, company_name = get_stock_symbol(stock)
        if not symbol: symbol = stock.upper(); company_name = stock.upper()
        
        metrics = fetch_financial_metrics(symbol)
        if not metrics:
            return {"error": f"Could not find any market data for '{stock}'. Please try a valid company name or ticker."}
            
        news = fetch_news(symbol)
        feed = []
        scores = []
        for item in news:
            lab, score = analyze_sentiment(item.get("title", ""))
            item.update({"sentiment": lab, "score": score, "source": "News"})
            feed.append(item)
            scores.append(score)
        avg_score = statistics.mean(scores) if scores else 0
        sentiment = "Positive" if avg_score > 0.05 else "Negative" if avg_score < -0.05 else "Neutral"
        return {"symbol": symbol, "company_name": company_name, "metrics": metrics, "feed": feed, "overall_score": avg_score, "overall_sentiment": sentiment}
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
def chat(data: dict):
    query = data.get("query", "hi").lower()
    context = data.get("context", "")
    
    # Basic greeting handled by code for speed
    if query in ["hi", "hello", "hey"]:
        return {"response": "Hello! I am StockSense AI, your dedicated stock analyst. I can help you interpret financial metrics, news sentiment, and stock charts. What can I analyze for you today?"}

    try:
        response = chatbot(query, context)
        return {"response": response}
    except Exception as e:
        print(f"Chat error: {e}")
        return {"response": "I'm having trouble connecting to my brain right now. Please try again in a second!"}

@app.get("/history/{symbol}")
def history(symbol: str, period: str = "1mo"):
    try:
        interval = "5m" if period == "1d" else "1d"
        hist = yf.Ticker(symbol).history(period=period, interval=interval)
        
        if period == "1d":
            data = [{"date": d.strftime("%H:%M"), "close": round(row["Close"], 2)} for d, row in hist.iterrows()]
        else:
            data = [{"date": str(d.date()), "close": round(row["Close"], 2)} for d, row in hist.iterrows()]
            
        return {"data": data}
    except Exception as e:
        print(f"History error: {e}")
        return {"error": "no data"}

@app.get("/")
def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/{file_path:path}")
def serve_file(file_path: str):
    full_path = os.path.join(frontend_path, file_path)
    if os.path.isfile(full_path):
        return FileResponse(full_path)
    return FileResponse(os.path.join(frontend_path, "index.html"))