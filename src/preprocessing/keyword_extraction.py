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
    Extracts keywords from a list of texts using KeyBERT.

    Args:
        texts (List[str]): List of texts to extract keywords from.
        top_n (int): Number of top keywords to extract per text.

    Returns:
        It returns something else not a list of list of str.
        List[List[str]]: List of keyword lists for each text.
    """
    article_summaries = []
    documents = find_documents("News_Articles", {"id": {"$in": article_ids}})
    for doc in documents:
        article_summaries.append({"id": doc["id"], "summary": doc["summary"]})

    logger.info("Initializing KeyBERT model for keyword extraction.")
    model = KeyBERT("all-MiniLM-L6-v2")

    article_keywords = []
    logger.info(f"Extracting keywords from {len(article_summaries)} texts.")
    for idx, obj in enumerate(article_summaries):
        logger.debug(
            f"Extracting keywords from text {idx+1}/{len(article_summaries)}.")
        try:
            keywords = model.extract_keywords(
                obj.get("summary"),
                keyphrase_ngram_range=(1, 2),
                stop_words="english",
                top_n=top_n,
            )
            extracted_keywords = [kw[0] for kw in keywords]
            keyword_obj = {"id": obj.get("id"), "keywords": extracted_keywords}

            article_keywords.append(keyword_obj)
            append_to_document("News_Articles", {
                               "id": obj.get("id")}, keyword_obj)
            logger.debug(f"Keywords for text {idx+1}: {extracted_keywords}")
        except Exception as e:
            logger.error(f"Error extracting keywords from text {idx+1}: {e}")
            article_keywords.append([])
    logger.info("Keyword extraction completed.")

    # --------
    # MongoDB code to store article keywords
    # --------

    return article_keywords


# def aggregate_keywords(texts, top_n=10):
#     logger.info("Aggregating keywords across all articles.")
#     keywords = extract_keywords(texts, top_n)
#     logger.info(f"Top {top_n} aggregated keywords: {keywords}")
#     return keywords
