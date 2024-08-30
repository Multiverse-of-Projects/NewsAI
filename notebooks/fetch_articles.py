import requests
import json
# import set logger from the logger.py file
from src.utils.logger import setup_logger

logger = setup_logger()

filename = "articles.json"
all_articles = []

# Load existing data if the file exists
try:
    with open(filename, "r", encoding="utf-8") as f:
        all_articles = json.load(f)
except FileNotFoundError:
    logger.info(f"{filename} not found. A new file will be created.")
except json.JSONDecodeError:
    logger.warning(f"{filename} contains invalid JSON. Starting fresh.")

# Fetch new articles and append them to the list
for i in range(0, 5):
    url = f"https://api.mediastack.com/v1/news?access_key=b426b77ca4d08489aead616cca2cefd0&countries=in&languages=en&offset={i}"
    logger.debug("Requesting data from NewsAPI")
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()

    articles = data.get("data", [])
    if articles:
        all_articles.extend(articles)
        logger.info(f"Fetched and appended {len(articles)} articles.")
    else:
        logger.warning("No articles found in the response")

# Save all articles back to the file
try:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=4)
    logger.info(f"All articles stored in {filename}")
except Exception as e:
    logger.error(f"Error occurred while storing articles: {str(e)}")
