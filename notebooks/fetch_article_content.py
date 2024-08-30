import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from src.utils.logger import setup_logger

logger = setup_logger()

def fetch_article_content(url):
    try:
        # Send a GET request to the article URL
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors

        # Parse the content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the article content based on common HTML structure
        article_content = ""

        # Many articles have a <p> tag structure for paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            for p in paragraphs:
                article_content += p.get_text() + "\n"
        else:
            # Fallback if no <p> tags found, try another structure, e.g., <div>
            divs = soup.find_all('div')
            for div in divs:
                article_content += div.get_text() + "\n"

        # Optionally, clean up the content
        article_content = article_content.strip()

        return article_content

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch the article: {e}")
        return None

with open("articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

article_contents = []

for idx, article in enumerate(articles, start=1):
    title = article.get("title")
    description = article.get("description")
    url = article.get("url")
    published_at = article.get("published_at")

    # Fetch the article content using the URL
    article_content = fetch_article_content(url)

    # Create a new object with the required fields
    article_content_obj = {
        "id": idx,
        "title": title,
        "description": description,
        "url": url,
        "published_at": published_at,
        "article_content": article_content
    }

    # Add the new object to the list
    article_contents.append(article_content_obj)

# Save the new objects to article_content.json
with open("article_content.json", "w", encoding="utf-8") as f:
    json.dump(article_contents, f, ensure_ascii=False, indent=4)

print("Article content has been successfully saved to article_content.json")
article_content = fetch_article_content(url)
if article_content:
    logger.info("Article Content Extracted:\n")
    logger.info(article_content)
