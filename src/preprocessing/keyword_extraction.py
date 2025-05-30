from collections import defaultdict
from typing import List

import nltk
from keybert import KeyBERT
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from src.utils.dbconnector import append_to_document, find_documents
from src.utils.logger import setup_logger

nltk.download("punkt")
nltk.download("stopwords")

# Setup logger
logger = setup_logger()


# Not in use
def preprocess_text(text):
    """
    Preprocesses a given text by tokenizing it and removing stopwords.

    Args:
        text (str): The text to preprocess.

    Returns:
        List[str]: A list of words without stopwords.
    """

    logger.info("Preprocessing text for tokenization and stopword removal.")
    stop_words = set(stopwords.words("english"))
    try:
        words = word_tokenize(text)
    except Exception as e:
        logger.error("Error during tokenization: %s", e)
        return []
    filtered_words = [
        word for word in words if word.isalnum() and word.lower() not in stop_words
    ]
    logger.info("Text preprocessed successfully.")
    return filtered_words


# Not in use
def bert_keyword_extraction(texts: List[str], top_n: int = 10) -> List[str]:
    """
    Extracts keywords from a list of texts using KeyBERT.

    Args:
        texts (List[str]): List of texts to extract keywords from.
        top_n (int): Number of top keywords to extract per text.

    Returns:
        List[str]: List of unique extracted keywords.
    """
    logger.info("Starting keyword extraction using KeyBERT.")
    model = KeyBERT("all-MiniLM-L6-v2")

    all_keywords = []
    for text in texts:
        keywords = model.extract_keywords(
            text, keyphrase_ngram_range=(1, 2), top_n=top_n
        )
        all_keywords.extend([kw[0] for kw in keywords])

    logger.info("KeyBERT keyword extraction completed successfully.")
    return list(set(all_keywords))  # Return unique keywords


def extract_keywords(article_ids, top_n: int = 10):
    """
    Extracts keywords from article summaries using KeyBERT.

    Args:
        article_ids (List[str]): List of article IDs to extract keywords from.
        top_n (int): Number of top keywords to extract per text.

    Returns:
        List[dict]: List of dictionaries containing article IDs and their keywords.
    """
    article_summaries = []
    
    try:
        # Fetch documents from the database
        documents = find_documents("News_Articles", {"id": {"$in": article_ids}})
        for doc in documents:
            # Ensure summary exists and is a string
            summary = doc.get("summary", "")
            if not summary:
                logger.warning(f"Missing summary for article ID: {doc['id']}")
                summary = ""
            elif not isinstance(summary, str):
                logger.warning(f"Summary is not a string for article ID: {doc['id']}. Converting to string.")
                summary = str(summary)
                
            article_summaries.append({"id": doc["id"], "summary": summary})
    except Exception as e:
        logger.error(f"Error fetching articles from database: {e}")
        return []
    
    if not article_summaries:
        logger.warning("No valid article summaries found for keyword extraction")
        return []

    logger.info("Initializing KeyBERT model for keyword extraction.")
    try:
        model = KeyBERT("all-MiniLM-L6-v2")
    except Exception as e:
        logger.error(f"Failed to initialize KeyBERT model: {e}")
        return []

    article_keywords = []
    logger.info(f"Extracting keywords from {len(article_summaries)} texts.")
    
    for idx, obj in enumerate(article_summaries):
        article_id = obj.get("id")
        logger.debug(f"Extracting keywords from text {idx+1}/{len(article_summaries)} (ID: {article_id}).")
        
        # Skip empty summaries
        summary = obj.get("summary", "")
        if not summary:
            logger.warning(f"Skipping article {article_id} - empty summary")
            empty_keywords = {"id": article_id, "keywords": []}
            article_keywords.append(empty_keywords)
            append_to_document("News_Articles", {"id": article_id}, {"keywords": []})
            continue
            
        try:
            # Extract keywords from the summary
            keywords = model.extract_keywords(
                summary,
                keyphrase_ngram_range=(1, 2),
                stop_words="english",
                top_n=top_n,
            )
            extracted_keywords = [kw[0] for kw in keywords]
            keyword_obj = {"id": article_id, "keywords": extracted_keywords}
            
            article_keywords.append(keyword_obj)
            append_to_document("News_Articles", {"id": article_id}, {"keywords": extracted_keywords})
            logger.debug(f"Keywords for article {article_id}: {extracted_keywords}")
            
        except Exception as e:
            logger.error(f"Error extracting keywords from article {article_id}: {e}")
            # Save empty keywords to avoid repeated failed attempts
            article_keywords.append({"id": article_id, "keywords": []})
            append_to_document("News_Articles", {"id": article_id}, {"keywords": []})
    
    logger.info("Keyword extraction completed.")
    return article_keywords


# def aggregate_keywords(texts, top_n=10):
#     logger.info("Aggregating keywords across all articles.")
#     keywords = extract_keywords(texts, top_n)
#     logger.info(f"Top {top_n} aggregated keywords: {keywords}")
#     return keywords
