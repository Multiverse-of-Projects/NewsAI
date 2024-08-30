from src.utils.logger import setup_logger
from src.sentiment_analysis.sentiment_model import analyze_sentiments


# Setup logger
logger = setup_logger()

def classify_sentiments(texts):
    logger.info("Classifying sentiments of multiple articles.")
    results = {'positive': [], 'negative': [], 'neutral': []}
    
    for text in texts:
        sentiment = analyze_sentiment(text)
        label = sentiment[0]['label']
        score = sentiment[0]['score']
        
        if label == 'POSITIVE':
            results['positive'].append((text, score))
        elif label == 'NEGATIVE':
            results['negative'].append((text, score))
        else:
            results['neutral'].append((text, score))
    
    logger.info("Sentiment classification completed.")
    return results
