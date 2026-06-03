import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download required NLTK data
nltk.download('vader_lexicon', quiet=True)

def get_dance_style(text: str) -> str:
    """
    Determine dance style based on the sentiment of the input text.
    
    Logic:
    Positive sentiment -> "happy"
    Negative sentiment -> "sad"
    Neutral sentiment -> "normal"
    """
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(text)
    compound_score = sentiment_scores['compound']
    
    if compound_score >= 0.05:
        return "happy"
    elif compound_score <= -0.05:
        return "sad"
    else:
        return "normal"
