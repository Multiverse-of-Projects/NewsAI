import json
import os
import uuid
from datetime import datetime

import requests
from dotenv import load_dotenv

from src.utils.dbconnector import find_one_document, insert_document, update_document
from src.utils.logger import setup_logger

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

# Configure logger
logger = setup_logger()


def fetch_news(query, from_date, sort_by="popularity", limit=10, to_json=False, force_fetch=False):
    """
    Fetches news articles from NewsAPI for the given query, from date and sort_by.

    Args:
        query (str): The query to search for in the NewsAPI.
        from_date (str or datetime): The date from which to fetch the articles.
        sort_by (str): The field to sort the results by.
        limit (int): The number of articles to fetch.
        to_json (bool): Whether to store the results in a JSON file.
        force_fetch (bool): Whether to bypass the cache and fetch new results.

    Returns:
        List[str]: The IDs of the articles that were fetched and stored in MongoDB.
    """
    # Check for cached results first
    try:
        logger.debug("Requesting data from NewsAPI")
        previous = find_one_document("News_Articles_Ids", {"query": query})
        existing_ids = []
        
        if previous and not force_fetch:
            logger.info(f"Previous data found for {query} from {from_date}")
            return previous["ids"]
        elif previous and force_fetch:
            # Keep track of existing IDs to avoid duplicates
            existing_ids = previous["ids"]
            logger.info(f"Found {len(existing_ids)} existing articles for {query}. Will fetch more up to {limit} total.")
            
        # Set up the API request
        base_url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "from": from_date,
            "sortBy": sort_by,
            "pageSize": limit
        }
        
        headers = {
            "X-Api-Key": API_KEY,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json"
        }
        
        # Make the request
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        if data.get("status") == "ok":
            logger.info(f"Total results from NewsAPI: {data.get('totalResults')}")
            
            # Log the titles of returned articles for debugging
            logger.info("Articles returned from NewsAPI:")
            for i, article in enumerate(data.get("articles", [])[:limit]):
                logger.info(f"  {i+1}. {article.get('title')}")
                
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
                return []
            else:
                # Initialize lists for article objects and IDs
                articles_db = []
                article_ids = []
                
                # If we have existing IDs and are forcing a fetch, start with those
                if existing_ids and force_fetch:
                    article_ids = existing_ids.copy()
                
                # Set of URLs and titles already in our database to avoid duplicates
                existing_urls = set()
                existing_titles = set()
                if article_ids:
                    # Get URLs and titles of existing articles
                    for aid in article_ids:
                        article = find_one_document("News_Articles", {"id": aid})
                        if article:
                            if "url" in article:
                                existing_urls.add(article["url"])
                            if "title" in article:
                                existing_titles.add(article["title"])
                
                duplicates_by_url = 0
                duplicates_by_title = 0
                
                # Process articles from the API response
                for article in data.get("articles", []):
                    # Skip if we've reached the limit
                    if len(article_ids) >= limit:
                        logger.info(f"Reached limit of {limit} articles. Stopping.")
                        break
                    
                    title = article.get("title")
                    url = article.get("url")
                    
                    # Skip duplicates based on URL
                    if url in existing_urls:
                        duplicates_by_url += 1
                        logger.debug(f"Skipping duplicate article (by URL): {title}")
                        continue
                    
                    # Skip duplicates based on title (if title is not None)
                    if title and title in existing_titles:
                        duplicates_by_title += 1
                        logger.debug(f"Skipping duplicate article (by title): {title}")
                        continue
                    
                    # Generate ID and add to database
                    id = str(uuid.uuid4())
                    article_ids.append(id)
                    
                    # Update sets of existing URLs and titles
                    if url:
                        existing_urls.add(url)
                    if title:
                        existing_titles.add(title)
                    
                    article_obj = {
                        "id": id,
                        "title": title,
                        "description": article.get("description"),
                        "url": url,
                        "urltoimage": article.get("urlToImage"),
                        "publishedat": article.get("publishedAt"),
                        "source": article.get("source").get("name"),
                    }
                    insert_document("News_Articles", article_obj)
                    articles_db.append(article_obj)

                logger.info(f"Total articles saved: {len(articles_db)}")
                if duplicates_by_url > 0 or duplicates_by_title > 0:
                    logger.info(f"Duplicates skipped: {duplicates_by_url} by URL, {duplicates_by_title} by title")
                logger.debug(f"Article IDs: {article_ids}")
                
                # Update or insert the document in News_Articles_Ids
                if previous:
                    # Update document logic
                    update_document("News_Articles_Ids", {"query": query}, {"ids": article_ids})
                    logger.info(f"Updated News_Articles_Ids for query '{query}' with {len(article_ids)} articles")
                else:
                    insert_document("News_Articles_Ids", {"query": query, "ids": article_ids})
                    logger.info(f"Inserted new entry in News_Articles_Ids for query '{query}' with {len(article_ids)} articles")
                
                return article_ids
        else:
            logger.error(f"Error in response: {data}")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP Request failed: {type(e).__name__} - {str(e)}")
        return []  # Return empty list to prevent errors


if __name__ == "__main__":
    # if __name__ == "__main__" and __package__ is None:
    __package__ = "src.ingestion"
    fetch_news(
        query="Kolkata Murder case",
        from_date="2024-08-21",
        sort_by="popularity",
        to_json=True,
    )
