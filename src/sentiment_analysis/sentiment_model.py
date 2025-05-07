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
    article_obj = []
    
    try:
        # Fetch documents from the database
        documents = find_documents("News_Articles", {"id": {"$in": article_ids}})
        for doc in documents:
            # Use summary for sentiment analysis if available, otherwise use content
            text_content = doc.get("summary", doc.get("content", ""))
            
            # Ensure content is a string
            if not isinstance(text_content, str):
                logger.warning(f"Content is not a string for article ID: {doc['id']}. Converting to string.")
                text_content = str(text_content) if text_content else ""
                
            if not text_content.strip():
                logger.warning(f"Empty content for article ID: {doc['id']}")
                
            article_obj.append({
                "id": doc["id"],
                "title": doc.get("title", ""),
                "text_content": text_content
            })
    except Exception as e:
        logger.error(f"Error fetching articles from database: {e}")
        return []
    
    if not article_obj:
        logger.warning("No valid articles found for sentiment analysis")
        return []

    logger.info("Initializing sentiment analysis pipeline.")
    try:
        sentiment_analyzer = pipeline(
            "sentiment-analysis", 
            model="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )
    except Exception as e:
        logger.error(f"Failed to initialize sentiment analysis pipeline: {e}")
        return []

    article_sentiments = []
    logger.info(f"Analyzing sentiments for {len(article_obj)} texts.")
    
    for idx, obj in enumerate(article_obj):
        article_id = obj.get("id")
        logger.debug(f"Analyzing sentiment for text {idx+1}/{len(article_obj)} (ID: {article_id}).")
        
        # Skip empty text content
        text_content = obj.get("text_content", "").strip()
        if not text_content:
            logger.warning(f"Skipping article {article_id} - empty text content")
            empty_sentiment = {
                "id": article_id,
                "sentiment": "UNKNOWN", 
                "sentiment_score": 0.0
            }
            article_sentiments.append(empty_sentiment)
            append_to_document("News_Articles", {"id": article_id}, empty_sentiment)
            continue
            
        try:
            # Truncate text to fit model constraints (typically 512 tokens)
            truncated_text = text_content[:500]  
            
            # Perform sentiment analysis - IMPORTANT: pass truncated_text as INPUTS parameter (not text)
            analysis = sentiment_analyzer(inputs=truncated_text)
            
            sentiment_obj = {
                "id": article_id,
                "sentiment": analysis[0]["label"],
                "sentiment_score": analysis[0]["score"],
            }
            
            article_sentiments.append(sentiment_obj)
            append_to_document("News_Articles", {"id": article_id}, sentiment_obj)
            logger.debug(f"Sentiment for article {article_id}: {sentiment_obj}")
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment for article {article_id}: {e}")
            # Save unknown sentiment to avoid repeated failed attempts
            unknown_sentiment = {
                "id": article_id,
                "sentiment": "UNKNOWN", 
                "sentiment_score": 0.0
            }
            article_sentiments.append(unknown_sentiment)
            append_to_document("News_Articles", {"id": article_id}, unknown_sentiment)

    logger.info("Sentiment analysis completed.")
    return article_sentiments


if __name__ == "__main__":
    # Test the function
    text = "A female trainee doctor was found dead in a seminar hall at a Kolkata hospital, sparking outrage and protests demanding safety for medical professionals. The incident, believed to be rape and murder, highlights the alarming security risks faced by doctors and nurses, particularly women, in India's government hospitals.  Lack of designated rest rooms, unrestricted access to wards, and a lack of background checks for volunteers contribute to the vulnerability. Despite calls for stricter federal laws and increased security measures, many doctors remain pessimistic, feeling resigned to working in unsafe conditions.  The article highlights the pervasive issue of violence against healthcare workers in India, with doctors often facing threats and assaults from patients, their relatives, and even hospital staff."
    analyze_sentiments([{"id": 1, "summary": text}])
