import json
from src.ingestion.fetch_articles import fetch_article_content
from src.ingestion.newsapi import fetch_news
from src.preprocessing.keyword_extraction import (bert_keyword_extraction,
                                                  extract_keywords)
from src.preprocessing.summarization import summarize_texts
from src.sentiment_analysis.classify import (analyze_sentiments,
                                             classify_sentiments)
from src.sentiment_analysis.wordcloud import generate_wordcloud
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()


def process_articles(query):
    logger.info("Starting the processing of articles.")

    # Fetch articles from NewsAPI
    article_ids = fetch_news(
        query=query, from_date="2024-08-01", sort_by="popularity", to_json=False
    )

    # Get contents for each article
    article_contents = fetch_article_content(article_ids)

    # contents_file = f"{query.replace(' ', '_')}_contents2.json"
    # with open(contents_file, "w", encoding="utf-8") as f:
    #     json.dump(article_contents, f, ensure_ascii=False, indent=4)

    #Summarize the articles
    logger.info("Summarizing articles.")
    article_summaries = summarize_texts(article_contents)

    # summaries_file = f"{query.replace(' ', '_')}_summaries2.json"
    # with open(summaries_file, "w", encoding="utf-8") as f:
    #     json.dump(article_summaries, f, ensure_ascii=False, indent=4)

    #Extract keywords from summaries
    logger.info("Extracting keywords from summaries.")
    article_keywords = extract_keywords(article_summaries, top_n=10)

    # keywords_file = f"{query.replace(' ', '_')}_keywords2.json"
    # with open(keywords_file, "w", encoding="utf-8") as f:
    #     json.dump(article_keywords, f, ensure_ascii=False, indent=4)

    # Analyze sentiments of summaries
    logger.info("Analyzing sentiments of summaries.")
    article_sentiments = analyze_sentiments(article_ids)

    # sentiments_file = f"{query.replace(' ', '_')}_sentiments2.json"
    # with open(sentiments_file, "w", encoding="utf-8") as f:
    #     json.dump(article_sentiments, f, ensure_ascii=False, indent=4)


    # # Extract keywords from summaries
    # logger.info("Extracting keywords from summaries.")
    # keywords_list = extract_keywords(summaries, top_n=10)

    # # Analyze sentiments of summaries
    # logger.info("Analyzing sentiments of summaries.")
    # sentiments = analyze_sentiments(summaries)

    # # Generate word clouds for each sentiment category
    # logger.info("Generating word clouds for sentiment categories.")
    # sentiment_categories = {"POSITIVE": [], "NEGATIVE": [], "NEUTRAL": []}

    # for keywords, sentiment in zip(keywords_list, sentiments):
    #     label = sentiment["label"].upper()
    #     if label in sentiment_categories:
    #         sentiment_categories[label].extend(keywords)
    #     else:
    #         sentiment_categories["NEUTRAL"].extend(keywords)

    # for sentiment_label, keywords in sentiment_categories.items():
    #     if keywords:
    #         wordcloud = generate_wordcloud(keywords, sentiment_label)
    #     else:
    #         logger.warning(
    #             f"No keywords available for {sentiment_label} sentiment to generate word cloud."
    #         )

    # logger.info("Article processing pipeline completed successfully.")
    # return keywords_list, sentiments, wordcloud


if __name__ == "__main__":
    logger.info("Starting the processing of articles.")

    process_articles("Kolkata Murder Case")

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
