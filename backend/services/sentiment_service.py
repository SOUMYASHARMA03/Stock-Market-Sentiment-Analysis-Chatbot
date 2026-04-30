import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    score = sia.polarity_scores(text)["compound"]
    
    if score > 0.05:
        return "Positive", score
    elif score < -0.05:
        return "Negative", score
    else:
        return "Neutral", score