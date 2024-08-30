from src.ingestion.fetch_articles import fetch_articles_contents
from src.ingestion.newsapi import fetch_news
from src.preprocessing.keyword_extraction import bert_keyword_extraction, extract_keywords
from src.sentiment_analysis.wordcloud import generate_wordcloud
from src.sentiment_analysis.classify import classify_sentiments, analyze_sentiments
from src.preprocessing.summarization import summarize_texts
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()


def process_articles(urls):
    logger.info("Starting the processing of articles.")

    # Fetch article contents
    contents = fetch_articles_contents(urls)

    logger.info("Summarizing articles.")
    summaries = summarize_texts(contents)
    
    # Extract keywords from summaries
    logger.info("Extracting keywords from summaries.")
    keywords_list = extract_keywords(summaries, top_n=10)
    
    # Analyze sentiments of summaries
    logger.info("Analyzing sentiments of summaries.")
    sentiments = analyze_sentiments(summaries)
    
    # Generate word clouds for each sentiment category
    logger.info("Generating word clouds for sentiment categories.")
    sentiment_categories = {'POSITIVE': [], 'NEGATIVE': [], 'NEUTRAL': []}
    
    for keywords, sentiment in zip(keywords_list, sentiments):
        label = sentiment['label'].upper()
        if label in sentiment_categories:
            sentiment_categories[label].extend(keywords)
        else:
            sentiment_categories['NEUTRAL'].extend(keywords)
    
    for sentiment_label, keywords in sentiment_categories.items():
        if keywords:
            wordcloud = generate_wordcloud(keywords, sentiment_label)
        else:
            logger.warning(f"No keywords available for {sentiment_label} sentiment to generate word cloud.")
    
    logger.info("Article processing pipeline completed successfully.")
    return keywords_list, sentiments, wordcloud


if __name__ == "__main__":
    logger.info("Starting the processing of articles.")

    # Fetch article contents
    news_data = fetch_news(
        query="Kolkata Murder Case", from_date="2024-08-25", to_json=False
    )
    urls = [article.get("url") for article in news_data.get("articles", [])]

    # Process articles
    keywords,sentiments, wordcloud = process_articles(urls)
    logger.info(f"Keywords: {keywords}")
    logger.info(f"Sentiments: {sentiments}")
    wordcloud.to_image().save("wordcloud.png")
    logger.info("Processing of articles completed successfully.")
