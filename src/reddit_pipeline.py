import os
import sys

from utils.logger import setup_logger

logger = setup_logger()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.ingestion.prawapi import fetch_reddit_posts_by_keyword
from src.preprocessing.reddit_posts_preprocessing import process_reddit_data
from src.sentiment_analysis.reddit_analysis import (sentiment_analysis,
                                                    summarize_content)


def user_sentiment_analysis():
    filename = fetch_reddit_posts_by_keyword(keyword="bombay", limit=3)

    content, all_comments = process_reddit_data(filename)

    summarized_content = summarize_content(content)
    return sentiment_analysis(summarized_content, all_comments)


if __name__ == "__main__":
    logger.info("Starting the process.")
    result = user_sentiment_analysis()
    print(result)
