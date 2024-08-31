import json
import os
import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.utils.logger import setup_logger

logger = setup_logger()


def fetch_article_content(article_ids):
    urls = []  # List of article ID and associated URL {id: url} using article_ids
    # ---------
    # MongoDB code to fetch URLs from the database
    # ---------
    with open("articles.json", "r", encoding="utf-8") as f:
        articles = json.load(f)
        for article in articles:
            id = article["id"]
            url = article["url"]
            urls.append({"id": id, "url": url})

    article_contents = []
    for obj in urls:
        id = obj["id"]
        url = obj["url"]
        try:
            # Send a GET request to the article URL
            response = requests.get(url)
            response.raise_for_status()  # Check for HTTP errors

            # Parse the content using BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract the article content based on common HTML structure
            article_content = ""

            # Many articles have a <p> tag structure for paragraphs
            paragraphs = soup.find_all("p")
            if paragraphs:
                for p in paragraphs:
                    article_content += p.get_text() + "\n"
            else:
                # Fallback if no <p> tags found, try another structure, e.g., <div>
                divs = soup.find_all("div")
                for div in divs:
                    article_content += div.get_text() + "\n"

            # Optionally, clean up the content
            article_content = article_content.strip()

            article_obj = {"id": id, "content": article_content}
            article_contents.append(article_obj)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch the article: {e}")
            return None

    logger.info(f"Total articles content fetched: {len(article_contents)}")
    # ---------
    # MongoDB code to store article content
    # ---------
    return article_contents


if __name__ == "__main__":
    url = "https://www.rt.com/india/602908-reclaiming-night-protests-over-rape/"
    article_content = fetch_article_content(url)
    if article_content:
        logger.info("Article Content Extracted:\n")
        logger.info(article_content)
