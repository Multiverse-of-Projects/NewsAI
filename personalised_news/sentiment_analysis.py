from transformers import pipeline

# Pre-trained sentiment analysis model
sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

def analyze_emotion(text):
    result = sentiment_pipeline(text)
    emotion = result[0]['label'].lower()
    return emotion  # Will return 'positive', 'negative', or 'neutral' as default
