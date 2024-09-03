import json
import asyncio
from aiohttp import ClientSession
from tenacity import retry, stop_after_attempt, wait_fixed
from concurrent.futures import ThreadPoolExecutor
from src.ingestion.fetch_articles import fetch_article_content
from src.ingestion.newsapi import fetch_news
from src.preprocessing.keyword_extraction import (bert_keyword_extraction,
                                                  extract_keywords)
from src.preprocessing.summarization import summarize_texts
from src.sentiment_analysis.classify import (analyze_sentiments,
                                             classify_sentiments)
from src.sentiment_analysis.wordcloud import generate_wordcloud
from src.utils.logger import setup_logger
from src.utils.dbconnector import append_to_document, content_manager

# Setup logger
logger = setup_logger()


# Assumed to be async functions (you may need to modify the actual implementations accordingly)
async def fetch_article_content_async(article_ids, session):
    tasks = [fetch_article_content(article_id, session) for article_id in article_ids]
    return await asyncio.gather(*tasks, return_exceptions=True)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(6))  # Retry logic for Gemini API
async def summarize_texts_async(articles_id):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, summarize_texts, articles_id)

async def extract_keywords_async(article_ids):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, extract_keywords, article_ids)

async def analyze_sentiments_async(article_ids):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, analyze_sentiments, article_ids)

async def process_articles_async(query, limit=10):
    logger.info("Starting the processing of articles.")
    article_ids = fetch_news(
        query=query,
        from_date="2024-08-04",
        sort_by="popularity",
        limit=limit,
        to_json=False,
    )
    if not isinstance(article_ids, list):
        raise ValueError("article_ids should be a list")

    async with ClientSession() as session:
        for article_id in article_ids:
            # Check the presence of content, summary, keywords, and sentiment in the DB
            field_status = content_manager(article_id, ["content", "summary", "keywords", "sentiment"])

            # Fetch content only if not already present
            if not field_status["content"]:
                content = await fetch_article_content_async(article_id, session)
                # Save content to MongoDB
                # append_to_document("News_Articles", {"id": article_id}, {"content": content})
            else:
                logger.info(f"Content already exists for article {article_id}. Skipping fetch.")

            # Summarize only if summary is not already present
            if not field_status["summary"]:
                summary = await summarize_texts_async([article_id])
            else:
                logger.info(f"Summary already exists for article {article_id}. Skipping summarization.")

            # Extract keywords only if not already present
            if not field_status["keywords"]:
                keywords = await extract_keywords_async([article_id])
            else:
                logger.info(f"Keywords already exist for article {article_id}. Skipping extraction.")

            # Analyze sentiment only if not already present
            if not field_status["sentiment"]:
                sentiment = await analyze_sentiments_async([article_id])
            else:
                logger.info(f"Sentiment already exists for article {article_id}. Skipping sentiment analysis.")

    logger.info("Processing completed.")
    return article_ids


def process_articles(query, limit=10):
    logger.info("Starting the processing of articles.")
    asyncio.run(process_articles_async(query, limit))
    return
    # Fetch articles from NewsAPI
    article_ids = fetch_news(
        query=query,
        from_date="2024-08-04",
        sort_by="popularity",
        limit=limit,
        to_json=False,
    )
    if not isinstance(article_ids, list):
        raise ValueError("article_ids should be a list")

    # Get contents for each article
    article_contents = fetch_article_content(article_ids)

    # contents_file = f"{query.replace(' ', '_')}_contents2.json"
    # with open(contents_file, "w", encoding="utf-8") as f:
    #     json.dump(article_contents, f, ensure_ascii=False, indent=4)

    # Summarize the articles
    logger.info("Summarizing articles.")
    article_summaries = summarize_texts(article_ids)

    # summaries_file = f"{query.replace(' ', '_')}_summaries2.json"
    # with open(summaries_file, "w", encoding="utf-8") as f:
    #     json.dump(article_summaries, f, ensure_ascii=False, indent=4)

    # Extract keywords from summaries
    logger.info("Extracting keywords from summaries.")
    article_keywords = extract_keywords(article_ids, top_n=10)

    # keywords_file = f"{query.replace(' ', '_')}_keywords2.json"
    # with open(keywords_file, "w", encoding="utf-8") as f:
    #     json.dump(article_keywords, f, ensure_ascii=False, indent=4)

    # Analyze sentiments of summaries
    logger.info("Analyzing sentiments of summaries.")
    article_sentiments = analyze_sentiments(article_ids)



if __name__ == "__main__":
    logger.info("Starting the processing of articles.")

    process_articles("Reliance Industries", limit=1000)

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
