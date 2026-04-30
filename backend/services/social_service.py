import random

def fetch_social_sentiment(symbol):
    """
    Mocks social media sentiment data (e.g., from Reddit/Twitter).
    """
    mock_posts = [
        {"text": f"Just bought more {symbol}, to the moon! 🚀", "sentiment": "Positive", "score": random.uniform(0.6, 0.99)},
        {"text": f"Earnings report for {symbol} looks terrible, dumping my bags.", "sentiment": "Negative", "score": random.uniform(-0.99, -0.5)},
        {"text": f"{symbol} is trading sideways today.", "sentiment": "Neutral", "score": random.uniform(-0.1, 0.1)},
        {"text": f"Everyone is talking about {symbol} right now on WallStreetBets.", "sentiment": "Positive", "score": random.uniform(0.3, 0.8)},
        {"text": f"The new product launch from {symbol} was a huge disappointment.", "sentiment": "Negative", "score": random.uniform(-0.9, -0.4)}
    ]
    
    # Shuffle and pick a random subset to simulate real-time varying data
    random.shuffle(mock_posts)
    return mock_posts[:3]
