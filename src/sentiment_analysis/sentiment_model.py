from typing import Dict, List

from transformers import pipeline

from src.utils.dbconnector import append_to_document, find_documents
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()


def analyze_sentiments(article_ids: List[str]) -> List[Dict[str, float]]:
    """
    Analyze the sentiment of a list of article IDs.

    Args:
        article_ids (List[str]): List of article IDs to analyze.

    Returns:
        List[Dict[str, float]]: List of sentiment analysis results for each text.
    """
    article_obj = []  # This object should have id, title and description
    documents = find_documents("News_Articles", {"id": {"$in": article_ids}})
    for doc in documents:
        article_obj.append(
            {
                "id": doc["id"],
                "title": doc["title"],
                "description": doc.get("content", ""),
            }
        )

    logger.info("Initializing sentiment analysis pipeline.")
    sentiment_analyzer = pipeline(
        "sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest"
    )

    article_sentiments = []
    logger.info(f"Analyzing sentiments for {len(article_obj)} texts.")
    for idx, obj in enumerate(article_obj):
        logger.debug(
            f"Analyzing sentiment for text {idx+1}/{len(article_obj)}.")
        try:
            analysis = sentiment_analyzer(obj.get("description")[:511])
            print("Analysis", analysis)
            sentiment_obj = {
                "id": obj.get("id"),
                "sentiment": analysis[0]["label"],
                "sentiment_score": analysis[0]["score"],
            }
            article_sentiments.append(sentiment_obj)
            append_to_document("News_Articles", {
                               "id": obj.get("id")}, sentiment_obj)
            logger.debug(f"Sentiment for text {idx+1}: {sentiment_obj}")

        except Exception as e:
            logger.error(f"Error analyzing sentiment for text {idx+1}: {e}")
            article_sentiments.append({"label": "UNKNOWN", "score": 0.0})
            append_to_document(
                "News_Articles",
                {"id": obj.get("id")},
                {"sentiment": "UNKNOWN", "sentiment_score": 0.0},
            )

    logger.info("Sentiment analysis completed.")
    return article_sentiments


if __name__ == "__main__":
    # Test the function
    text = "A female trainee doctor was found dead in a seminar hall at a Kolkata hospital, sparking outrage and protests demanding safety for medical professionals. The incident, believed to be rape and murder, highlights the alarming security risks faced by doctors and nurses, particularly women, in India's government hospitals.  Lack of designated rest rooms, unrestricted access to wards, and a lack of background checks for volunteers contribute to the vulnerability. Despite calls for stricter federal laws and increased security measures, many doctors remain pessimistic, feeling resigned to working in unsafe conditions.  The article highlights the pervasive issue of violence against healthcare workers in India, with doctors often facing threats and assaults from patients, their relatives, and even hospital staff."
    analyze_sentiments([{"id": 1, "summary": text}])
