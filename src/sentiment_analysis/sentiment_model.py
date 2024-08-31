from typing import Dict, List

from transformers import pipeline

from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()


def analyze_sentiments(article_summaries):
    """
    Analyzes sentiments of a list of texts.

    Args:
        texts (List[str]): List of texts to analyze.

    Returns:
        List[Dict[str, float]]: List of sentiment analysis results for each text.
    """
    logger.info("Initializing sentiment analysis pipeline.")
    sentiment_analyzer = pipeline("sentiment-analysis")

    article_sentiments = []
    logger.info(f"Analyzing sentiments for {len(article_summaries)} texts.")
    for idx, obj in enumerate(article_summaries):
        logger.debug(f"Analyzing sentiment for text {idx+1}/{len(article_summaries)}.")
        try:
            analysis = sentiment_analyzer(obj.get("summarized_content"))
            sentiment_obj = {"id": obj.get("id"), "sentiment": analysis[0]["label"], "sentiment_score": analysis[0]["score"]}
            article_sentiments.append(sentiment_obj)
            logger.debug(f"Sentiment for text {idx+1}: {sentiment_obj}")

        except Exception as e:
            logger.error(f"Error analyzing sentiment for text {idx+1}: {e}")
            article_sentiments.append({"label": "UNKNOWN", "score": 0.0})
            
    logger.info("Sentiment analysis completed.")
    return article_sentiments
