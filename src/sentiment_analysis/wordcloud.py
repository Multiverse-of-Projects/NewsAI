import matplotlib.pyplot as plt
from wordcloud import WordCloud

from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()


def generate_wordcloud(keywords, sentiment_label):
    logger.info(f"Generating word cloud for {sentiment_label} words.")
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
        " ".join(keywords)
    )
    return wordcloud
