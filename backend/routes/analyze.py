from fastapi import APIRouter, HTTPException
from backend.models.response_model import AnalyzeRequest, AnalyzeResponse
from backend.services.news_service import NewsService
from backend.services.ai_service import AIService
from backend.services.sentiment_service import SentimentService

router = APIRouter()
ai_service = AIService()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_stock_sentiment(request: AnalyzeRequest):
    try:
        news_articles = NewsService.get_stock_news(request.ticker)
        raw_ai_analysis = ai_service.analyze_sentiment(news_articles)
        processed_data = SentimentService.process_sentiment(raw_ai_analysis)
        
        return AnalyzeResponse(
            ticker=request.ticker.upper(),
            sentiment=processed_data["sentiment"],
            summary=processed_data["summary"],
            confidence=processed_data["confidence"],
            bot_response=processed_data["bot_response"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")