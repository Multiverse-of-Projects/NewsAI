import json
import os
import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from src.utils.dbconnector import append_to_document, find_documents

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.utils.dbconnector import content_manager
from src.utils.logger import setup_logger

logger = setup_logger()


import asyncio

import aiohttp
from bs4 import BeautifulSoup


async def fetch_article_content(article_ids, session):
    try:
        docs = find_documents("News_Articles", {"id": {"$in": article_ids}})
    except Exception as e:
        logger.error(f"Failed to find documents: {e}")
        raise

    urls_to_fetch = []

    # Check if content already exists for each article
    for doc in docs:
        id = doc["id"]
        url = doc["url"]

        # Use the content manager to check if content already exists
        field_status = content_manager(id, ["content"])

        if not field_status["content"]:
            urls_to_fetch.append({"id": id, "url": url})
            logger.info(f"Fetching content for article {id}")
        else:
            logger.info(f"Content already exists for article {id}. Skipping fetch.")

    article_contents = []

    # Define an asynchronous function to fetch content
    async def fetch_content(id, url):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                soup = BeautifulSoup(await response.text(), "html.parser")

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

                # Clean up the content
                article_content = article_content.strip()

                article_obj = {"id": id, "content": article_content}
                article_contents.append(article_obj)

                # Save content to MongoDB
                append_to_document("News_Articles", {"id": id}, article_obj)
                logger.info(f"Content fetched and saved for article {id}")
        except Exception as e:
            logger.error(f"Failed to fetch the article {id}: {e}")

    # Run the fetch operations in parallel using aiohttp
    tasks = [fetch_content(obj["id"], obj["url"]) for obj in urls_to_fetch]
    await asyncio.gather(*tasks)

    logger.info(f"Total articles content fetched: {len(article_contents)}")
    return article_contents


async def test_fetch_article_content():
    async with aiohttp.ClientSession() as session:
        contents = await fetch_article_content(article_ids, session)
        print(contents)  # Print the fetched content for verification


if __name__ == "__main__":
    url = "https://www.rt.com/india/602908-reclaiming-night-protests-over-rape/"
    article_ids = [
        "b01d85d7-d538-47cc-a7c4-31c13e7f6b4e",
        "15133cc7-1522-41f9-8db4-70568e837968",
    ]
    asyncio.run(test_fetch_article_content())
