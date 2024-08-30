from typing import Dict, List

from transformers import pipeline

from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

# Load a sentiment-analysis model
logger.info("Loading sentiment analysis model using BERT.")
# sentiment_analyzer = pipeline("sentiment-analysis")


def analyze_sentiments(texts: List[str]) -> List[Dict[str, float]]:
    """
    Analyzes sentiments of a list of texts.

    Args:
        texts (List[str]): List of texts to analyze.

    Returns:
        List[Dict[str, float]]: List of sentiment analysis results for each text.
    """
    logger.info("Initializing sentiment analysis pipeline.")
    sentiment_analyzer = pipeline("sentiment-analysis", model="sentiment-analysis")

    results = []
    logger.info(f"Analyzing sentiments for {len(texts)} texts.")
    for idx, text in enumerate(texts):
        logger.debug(f"Analyzing sentiment for text {idx+1}/{len(texts)}.")
        try:
            analysis = sentiment_analyzer(text)
            result = {"label": analysis[0]["label"], "score": analysis[0]["score"]}
            results.append(result)
            logger.debug(f"Sentiment for text {idx+1}: {result}")
        except Exception as e:
            logger.error(f"Error analyzing sentiment for text {idx+1}: {e}")
            results.append({"label": "UNKNOWN", "score": 0.0})
    logger.info("Sentiment analysis completed.")
    return results
