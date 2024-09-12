import json
import os
import uuid
from datetime import datetime

import requests
from dotenv import load_dotenv

from src.utils.dbconnector import find_one_document, insert_document
from src.utils.logger import setup_logger

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

# Configure logger
logger = setup_logger()


def fetch_news(query, from_date: datetime, sort_by, limit, to_json):
    """
    Fetches news articles from NewsAPI for the given query, from date and sort_by.

    Args:
        query (str): The query to search for in the NewsAPI.
        from_date (datetime.datetime): The date from which to fetch the articles.
        sort_by (str): The field to sort the results by.
        limit (int): The number of articles to fetch.
        to_json (bool): Whether to store the results in a JSON file.

    Returns:
        List[str]: The IDs of the articles that were fetched and stored in MongoDB.
    """
    url = f"https://newsapi.org/v2/everything?q={query}&from={from_date}&sortBy={sort_by}&apiKey={API_KEY}"
    try:
        logger.debug("Requesting data from NewsAPI")
        previous = find_one_document("News_Articles_Ids", {"query": query})
        if previous:
            logger.info(f"Previous data found for {query} from {from_date}")
            return previous["ids"]
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        if data.get("status") == "ok":
            logger.info(f"Total results: {data.get('totalResults')}")
            if to_json:
                try:
                    # store the data in json
                    # -----
                    filename = f"{query.replace(' ', '_')}_{from_date}.json"
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    logger.info(f"Results stored in {filename}")
                    # -----
                except Exception as e:
                    logger.error(
                        f"Error occurred while storing results: {str(e)}")
            else:
                articles_db = []
                article_ids = []
                for article in data.get("articles", [])[:limit]:
                    logger.debug(
                        f"Adding ids to articles and saving them to MongoDB")
                    id = str(uuid.uuid4())
                    article_ids.append(id)
                    article_obj = {
                        "id": id,
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "url": article.get("url"),
                        "urltoimage": article.get("urlToImage"),
                        "publishedat": article.get("publishedAt"),
                        "source": article.get("source").get("name"),
                    }
                    insert_document("News_Articles", article_obj)

                logger.info(f"Total articles saved: {len(articles_db)}")
                logger.debug(f"Article IDs: {article_ids}")
                insert_document(
                    "News_Articles_Ids", {"query": query, "ids": article_ids}
                )
                return article_ids
        else:
            logger.error(f"Error in response: {data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP Request failed: {type(e).__name__} - {str(e)}")


if __name__ == "__main__":
    # if __name__ == "__main__" and __package__ is None:
    __package__ = "src.ingestion"
    fetch_news(
        query="Kolkata Murder case",
        from_date="2024-08-21",
        sort_by="popularity",
        to_json=True,
    )
