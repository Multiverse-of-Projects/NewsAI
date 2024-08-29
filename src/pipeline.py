from src.ingestion.newsapi import fetch_news
from src.ingestion.fetch_articles import fetch_articles_contents
from src.preprocessing.keyword_extraction import aggregate_keywords
from src.sentiment_analysis.wordcloud import generate_wordcloud
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

def process_articles(urls):
    logger.info("Starting the processing of articles.")
    
    # Fetch article contents
    contents = fetch_articles_contents(urls)
    
    # Aggregate Keywords
    keywords = aggregate_keywords(contents, top_n=10)
    
    
    # Generate Word Clouds
    generate_wordcloud(keywords, "Positive")
    
    logger.info("Processing of articles completed successfully.")
    return keywords

if __name__ == "__main__":
    logger.info("Starting the processing of articles.")
    
    # Fetch article contents
    news_data = fetch_news(query="Kolkata Murder case", from_date="2024-08-21", to_json=False)
    urls = [article.get("url") for article in news_data.get("articles", [])]
    
    # Process articles
    process_articles(urls)
    
    logger.info("Processing of articles completed successfully.")
    
    