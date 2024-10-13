import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from aiohttp import ClientSession, ClientError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.ingestion.fetch_articles import fetch_article_content
from src.ingestion.newsapi import fetch_news
from src.preprocessing.keyword_extraction import (bert_keyword_extraction,
                                                  extract_keywords)
from src.preprocessing.summarization import summarize_texts
from src.sentiment_analysis.classify import (analyze_sentiments,
                                             classify_sentiments)
from src.sentiment_analysis.wordcloud import generate_wordcloud
from src.utils.dbconnector import append_to_document, content_manager, batch_insert_documents
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

# Define a dedicated ThreadPoolExecutor for CPU-bound tasks
cpu_bound_executor = ThreadPoolExecutor(max_workers=4)  # Adjust based on your CPU cores

# Retry configuration for transient errors
retry_decorator = retry(
    retry=retry_if_exception_type(ClientError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)

@retry_decorator
async def fetch_article_content_retry(article_ids, session):
    return await fetch_article_content(article_ids, session)

@retry_decorator
def summarize_texts_retry(article_ids):
    return summarize_texts(article_ids)

@retry_decorator
def extract_keywords_retry(article_ids):
    return extract_keywords(article_ids)

@retry_decorator
def analyze_sentiments_retry(article_ids):
    return analyze_sentiments(article_ids)

async def summarize_texts_async(article_id):
    """
    Asynchronous wrapper for summarize_texts.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(cpu_bound_executor, summarize_texts_retry, [article_id])

async def extract_keywords_async(article_id):
    """
    Asynchronous wrapper for extract_keywords.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(cpu_bound_executor, extract_keywords_retry, [article_id])

async def analyze_sentiments_async(article_id):
    """
    Asynchronous wrapper for analyze_sentiments.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(cpu_bound_executor, analyze_sentiments_retry, [article_id])

async def process_single_article_async(article_id, session, db_queue):
    """
    Process a single article asynchronously, including fetching content,
    summarizing, extracting keywords, analyzing sentiment, and batching DB inserts.
    """
    try:
        field_status = content_manager(
            article_id, ["content", "summary", "keywords", "sentiment"]
        )

        update_fields = {}

        # Fetch content only if not already present
        if not field_status["content"]:
            content = await fetch_article_content_retry([article_id], session)
            update_fields["content"] = content
            logger.info(f"Fetched content for article {article_id}.")
        else:
            logger.info(f"Content already exists for article {article_id}. Skipping fetch.")

        # Summarize only if summary is not already present
        if not field_status["summary"]:
            summary = await summarize_texts_async(article_id)
            update_fields["summary"] = summary
            logger.info(f"Summarized article {article_id}.")
        else:
            logger.info(f"Summary already exists for article {article_id}. Skipping summarization.")

        # Extract keywords only if not already present
        if not field_status["keywords"]:
            keywords = await extract_keywords_async(article_id)
            update_fields["keywords"] = keywords
            logger.info(f"Extracted keywords for article {article_id}.")
        else:
            logger.info(f"Keywords already exist for article {article_id}. Skipping extraction.")

        # Analyze sentiment only if not already present
        if not field_status["sentiment"]:
            sentiment = await analyze_sentiments_async(article_id)
            update_fields["sentiment"] = sentiment
            logger.info(f"Analyzed sentiment for article {article_id}.")
        else:
            logger.info(f"Sentiment already exists for article {article_id}. Skipping sentiment analysis.")

        if update_fields:
            # Queue the update for batch insertion
            db_queue.append({
                "filter": {"id": article_id},
                "update": {"$set": update_fields}
            })

        return article_id

    except Exception as e:
        logger.error(f"Error processing article {article_id}: {e}")
        return None

async def db_writer(db_queue):
    """
    Coroutine to write updates to the database in batches.
    """
    while True:
        if db_queue:
            batch = db_queue.copy()
            db_queue.clear()
            try:
                batch_insert_documents("News_Articles", batch)
                logger.info(f"Inserted batch of {len(batch)} documents into MongoDB.")
            except Exception as e:
                logger.error(f"Error inserting batch into MongoDB: {e}")
        await asyncio.sleep(1)  # Adjust the sleep time as needed

async def process_articles_async(query, limit=10):
    """
    Process a list of articles asynchronously with improved handling.
    """
    logger.info("Starting the processing of articles.")
    try:
        article_ids = fetch_news(
            query=query,
            from_date="2024-08-16",
            sort_by="popularity",
            limit=limit,
            to_json=False,
        )
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return []

    if not isinstance(article_ids, list):
        logger.error("article_ids should be a list")
        raise ValueError("article_ids should be a list")

    db_queue = []
    # Start the DB writer coroutine
    writer_task = asyncio.create_task(db_writer(db_queue))

    async with ClientSession() as session:
        tasks = [
            process_single_article_async(article_id, session, db_queue)
            for article_id in article_ids
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Wait a bit to ensure all DB operations are completed
    await asyncio.sleep(2)
    writer_task.cancel()
    try:
        await writer_task
    except asyncio.CancelledError:
        pass

    # Filter out any None results due to errors
    processed_article_ids = [aid for aid in results if aid is not None]

    logger.info("Processing completed.")
    return processed_article_ids

def process_articles(query, limit=10):
    """
    Synchronous entry point to process articles.
    """
    logger.info("Starting the processing of articles.")
    try:
        article_ids = asyncio.run(process_articles_async(query, limit))
    except Exception as e:
        logger.error(f"Error in processing articles: {e}")
        return []

    return article_ids

if __name__ == "__main__":
    logger.info("Starting the processing of articles.")

    article_ids = process_articles("Adani Hindenburg Report", limit=10)
    logger.info(f"Article IDs: {article_ids}")

    # Example of handling post-processing if needed
    # news_data = fetch_news(
    #     query="Kolkata Murder Case", from_date="2024-08-01", sort_by="popularity", to_json=False
    # )
    # urls = [article.get("url") for article in news_data.get("articles", [])]

    # # Process articles
    # keywords, sentiments, wordcloud = process_articles(urls)
    # logger.info(f"Keywords: {keywords}")
    # logger.info(f"Sentiments: {sentiments}")
    # wordcloud.to_image().save("wordcloud.png")
    # logger.info("Processing of articles completed successfully.")
