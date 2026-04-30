from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    """Schema for the incoming analysis request."""
    ticker: str = Field(..., description="The stock ticker symbol to analyze (e.g., AAPL)")

class AnalyzeResponse(BaseModel):
    """Schema for the outgoing structured response."""
    ticker: str = Field(..., description="The requested stock ticker symbol")
    sentiment: str = Field(..., description="Normalized sentiment: positive, negative, or neutral")
    summary: str = Field(..., description="AI-generated summary of the news")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")
    bot_response: str = Field(..., description="A friendly, conversational explanation of the analysis")