import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from aiohttp import ClientSession
from tenacity import retry, stop_after_attempt, wait_fixed

from src.ingestion.fetch_articles import fetch_article_content
from src.ingestion.newsapi import fetch_news
from src.preprocessing.keyword_extraction import bert_keyword_extraction, extract_keywords
from src.preprocessing.summarization import summarize_texts
from src.sentiment_analysis.classify import analyze_sentiments, classify_sentiments
from src.sentiment_analysis.wordcloud import generate_wordcloud
from src.utils.dbconnector import append_to_document, content_manager
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

async def summarize_texts_async(article_id):
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(None, summarize_texts, [article_id])
    except Exception as e:
        logger.error(f"Error summarizing text for article {article_id}: {e}")
        raise

async def extract_keywords_async(article_id):
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(None, extract_keywords, [article_id])
    except Exception as e:
        logger.error(f"Error extracting keywords for article {article_id}: {e}")
        raise

async def analyze_sentiments_async(article_id):
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(None, analyze_sentiments, [article_id])
    except Exception as e:
        logger.error(f"Error analyzing sentiment for article {article_id}: {e}")
        raise

async def process_single_article_async(article_id, session):
    try:
        field_status = content_manager(article_id, ["content", "summary", "keywords", "sentiment"])

        if not field_status["content"]:
            content = await fetch_article_content([article_id], session)
            # append_to_document("News_Articles", {"id": article_id}, {"content": content})
        else:
            logger.info(f"Content already exists for article {article_id}. Skipping fetch.")

        if not field_status["summary"]:
            if not field_status["content"]:
                content = await fetch_article_content([article_id], session)
            summary = await summarize_texts_async(article_id)
            # append_to_document("News_Articles", {"id": article_id}, {"summary": summary})
        else:
            logger.info(f"Summary already exists for article {article_id}. Skipping summarization.")

        if not field_status["keywords"]:
            keywords = await extract_keywords_async(article_id)
            # append_to_document("News_Articles", {"id": article_id}, {"keywords": keywords})
        else:
            logger.info(f"Keywords already exist for article {article_id}. Skipping extraction.")

        if not field_status["sentiment"]:
            sentiment = await analyze_sentiments_async(article_id)
            # append_to_document("News_Articles", {"id": article_id}, {"sentiment": sentiment})
        else:
            logger.info(f"Sentiment already exists for article {article_id}. Skipping sentiment analysis.")

        return article_id

    except Exception as e:
        logger.error(f"Error processing article {article_id}: {e}")
        raise

async def process_articles_async(query, limit=10):
    logger.info("Starting the processing of articles.")
    try:
        article_ids = fetch_news(query=query, from_date="2024-08-16", sort_by="popularity", limit=limit, to_json=False)
        if not isinstance(article_ids, list):
            raise ValueError("article_ids should be a list")

        async with ClientSession() as session:
            tasks = [process_single_article_async(article_id, session) for article_id in article_ids]
            await asyncio.gather(*tasks)

        logger.info("Processing completed.")
        return article_ids

    except Exception as e:
        logger.error(f"Error in process_articles_async: {e}")
        raise

def process_articles(query, limit=10):
    try:
        logger.info("Starting the processing of articles.")
        article_ids = asyncio.run(process_articles_async(query, limit))
        return article_ids
    except Exception as e:
        logger.error(f"Error in process_articles: {e}")
        raise

if __name__ == "__main__":
    try:
        logger.info("Starting the processing of articles.")
        article_ids = process_articles("Adani Hindenburg Report", limit=10)
        logger.info(f"Article IDs: {article_ids}")
    except Exception as e:
        logger.error(f"Unhandled error in main: {e}")
        print(f"An unexpected error occurred: {e}. Please check the logs.")
