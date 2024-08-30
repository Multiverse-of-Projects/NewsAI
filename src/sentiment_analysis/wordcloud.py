import matplotlib.pyplot as plt
from wordcloud import WordCloud
from typing import List

from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()


def generate_wordcloud(keywords: List[str], sentiment_label: str) -> WordCloud:
    logger.info(f"Generating word cloud for {sentiment_label} sentiment.")
    text = ' '.join(keywords)
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color="white", 
        colormap='viridis'
    ).generate(text)
    return wordcloud
