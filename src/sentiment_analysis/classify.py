from typing import Dict, List, Tuple

from src.sentiment_analysis.sentiment_model import analyze_sentiments
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()


def classify_sentiments(texts: List[str]) -> Dict[str, List[Tuple[str, float]]]:
    """
    Classify the sentiment of multiple texts.

    Args:
        texts (List[str]): List of text to classify sentiment for.

    Returns:
        Dict[str, List[Tuple[str, float]]]: Dictionary with three keys: 'positive', 'negative', 'neutral'.
            Each key maps to a list of tuples, where the first element of the tuple is the text and the second
            element is the sentiment score.
    """
    if not texts:
        raise ValueError("Input texts should not be empty.")
    logger.info("Classifying sentiments of multiple articles.")
    results = {"positive": [], "negative": [], "neutral": []}
    for text in texts:
        sentiment = analyze_sentiment(text)
        label = sentiment[0]["label"]
        score = sentiment[0]["score"]

        if label == "POSITIVE":
            results["positive"].append((text, score))
        elif label == "NEGATIVE":
            results["negative"].append((text, score))
        else:
            results["neutral"].append((text, score))

    logger.info("Sentiment classification completed.")
    return results
