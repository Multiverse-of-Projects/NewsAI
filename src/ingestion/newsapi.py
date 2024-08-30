import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

from src.utils.logger import setup_logger

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

# Configure logger
logger = setup_logger()


def fetch_news(query, from_date: datetime, to_json=True):
    url = f"https://newsapi.org/v2/everything?q={query}&from={from_date}&sortBy=popularity&apiKey={API_KEY}"
    try:
        logger.debug("Requesting data from NewsAPI")
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        if data.get("status") == "ok":
            logger.info(f"Total results: {data.get('totalResults')}")
            if to_json:
                try:
                    filename = f"{query.replace(' ', '_')}_{from_date}.json"
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    logger.info(f"Results stored in {filename}")
                except Exception as e:
                    logger.error(f"Error occurred while storing results: {str(e)}")
            else:
                for article in data.get("articles", []):
                    logger.debug(f"Article Title: {article.get('title')}")
                    try:
                        logger.debug(
                            f"Article Description: {article.get('description')}"
                        )
                    except UnicodeEncodeError:
                        logger.debug(
                            f"Article Description: {article.get('description').encode('utf-8').decode('ascii', 'ignore')}"
                        )
        else:
            logger.error(f"Error in response: {data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP Request failed: {type(e).__name__} - {str(e)}")


if __name__ == "__main__":
    # if __name__ == "__main__" and __package__ is None:
    __package__ = "src.ingestion"
    fetch_news(query="Kolkata Murder case", from_date="2024-08-21")
