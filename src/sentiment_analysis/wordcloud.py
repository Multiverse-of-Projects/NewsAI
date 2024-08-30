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

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title(f"{sentiment_label.capitalize()} Word Cloud")
    plt.show()
    logger.info(f"Word cloud for {sentiment_label} generated successfully.")
