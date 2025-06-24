from transformers import pipeline

# Load a sentiment-analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

def analyze_sentiment(article_text: str):
    result = sentiment_pipeline(article_text)[0]
    return {"label": result["label"], "score": result["score"]}
