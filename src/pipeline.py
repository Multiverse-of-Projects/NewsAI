import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from motor.motor_asyncio import AsyncIOMotorClient  # For async MongoDB operations

from aiohttp import ClientSession, ClientError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.ingestion.fetch_articles import fetch_article_content
from src.ingestion.newsapi import fetch_news
from src.preprocessing.keyword_extraction import (extract_keywords)
from src.preprocessing.summarization import summarize_texts
from src.sentiment_analysis.classify import analyze_sentiments
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

# Define a dedicated ThreadPoolExecutor for CPU-bound tasks
cpu_bound_executor = ThreadPoolExecutor(max_workers=4)

# Retry configuration for transient errors
retry_decorator = retry(
    retry=retry_if_exception_type(ClientError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)

# TokenBucket Class
class TokenBucket:
    def __init__(self, tokens, fill_rate):
        self.capacity = tokens  # Maximum number of tokens in the bucket
        self.tokens = tokens    # Current number of tokens in the bucket
        self.fill_rate = fill_rate  # Refill rate in tokens per second
        self.timestamp = time.monotonic()

    def consume(self, num_tokens=1):
        current_time = time.monotonic()
        elapsed = current_time - self.timestamp
        self.timestamp = current_time
        self.tokens = min(self.capacity, self.tokens + elapsed * self.fill_rate)

        if self.tokens >= num_tokens:
            self.tokens -= num_tokens
            return True
        else:
            return False

    async def wait_for_token(self, num_tokens=1):
        while not self.consume(num_tokens):
            await asyncio.sleep(0.1)  # Sleep for a short time before trying again

# Define the token bucket for rate-limited API calls (e.g., 10 requests/minute)
token_bucket = TokenBucket(tokens=10, fill_rate=1/6)  # 1 token every 6 seconds (10 per minute)

# Motor async MongoDB client
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["NewsDB"]

# Modular Pipeline Manager Class
class PipelineManager:
    def __init__(self, db_queue):
        self.db_queue = db_queue
        self.failed_articles = []

    async def fetch_content(self, article_id, session):
        await token_bucket.wait_for_token()  # Ensure we're respecting API rate limits
        content = await fetch_article_content_retry([article_id], session)
        if content:
            logger.info(f"Fetched content for article {article_id}.")
            return {"content": content}
        else:
            logger.warning(f"Failed to fetch content for article {article_id}.")
            self.failed_articles.append(article_id)
            return None

    async def summarize_content(self, article_id):
        summary = await summarize_texts_async(article_id)
        logger.info(f"Summarized article {article_id}.")
        return {"summary": summary}

    async def extract_keywords(self, article_id):
        keywords = await extract_keywords_async(article_id)
        logger.info(f"Extracted keywords for article {article_id}.")
        return {"keywords": keywords}

    async def analyze_sentiment(self, article_id):
        sentiment = await analyze_sentiments_async(article_id)
        logger.info(f"Analyzed sentiment for article {article_id}.")
        return {"sentiment": sentiment}

    async def process_single_article_async(self, article_id, session):
        """
        Process a single article asynchronously, including fetching content,
        summarizing, extracting keywords, analyzing sentiment, and batching DB inserts.
        """
        try:
            field_status = await db["News_Articles"].find_one({"id": article_id}, {"content", "summary", "keywords", "sentiment"})
            update_fields = {}

            # Step 1: Fetch content
            if not field_status or not field_status.get("content"):
                content = await self.fetch_content(article_id, session)
                if content:
                    update_fields.update(content)
                else:
                    return  # Skip further processing if content fetch failed

            # Step 2: Summarize content
            if not field_status or not field_status.get("summary"):
                summary = await self.summarize_content(article_id)
                update_fields.update(summary)

            # Step 3: Extract keywords
            if not field_status or not field_status.get("keywords"):
                keywords = await self.extract_keywords(article_id)
                update_fields.update(keywords)

            # Step 4: Analyze sentiment
            if not field_status or not field_status.get("sentiment"):
                sentiment = await self.analyze_sentiment(article_id)
                update_fields.update(sentiment)

            # Step 5: Queue the update for batch insertion
            if update_fields:
                self.db_queue.append({
                    "filter": {"id": article_id},
                    "update": {"$set": update_fields}
                })

            return article_id

        except Exception as e:
            logger.error(f"Error processing article {article_id}: {e}")
            self.failed_articles.append(article_id)
            return None

    async def db_writer(self):
        """
        Coroutine to write updates to the database in batches.
        """
        while True:
            if self.db_queue:
                batch = self.db_queue.copy()
                self.db_queue.clear()
                try:
                    await db["News_Articles"].bulk_write([
                        {"update_one": {
                            "filter": entry["filter"],
                            "update": entry["update"],
                            "upsert": True
                        }} for entry in batch
                    ])
                    logger.info(f"Inserted batch of {len(batch)} documents into MongoDB.")
                except Exception as e:
                    logger.error(f"Error inserting batch into MongoDB: {e}")
            await asyncio.sleep(1)  # Adjust the sleep time as needed

# Helper functions
async def summarize_texts_async(article_id):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(cpu_bound_executor, summarize_texts_retry, [article_id])

async def extract_keywords_async(article_id):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(cpu_bound_executor, extract_keywords_retry, [article_id])

async def analyze_sentiments_async(article_id):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(cpu_bound_executor, analyze_sentiments_retry, [article_id])

# Main processing function
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
    manager = PipelineManager(db_queue)

    # Start the DB writer coroutine
    writer_task = asyncio.create_task(manager.db_writer())

    async with ClientSession() as session:
        tasks = [
            manager.process_single_article_async(article_id, session)
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

    logger.info("Processing completed. Failed articles: %s", manager.failed_articles)
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
