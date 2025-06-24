from typing import List

import matplotlib.pyplot as plt
from wordcloud import WordCloud
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

def generate_wordcloud(keywords: List[str], sentiment_label: str) -> WordCloud:
    """
    Generates a word cloud for the given list of keywords and sentiment label.

    Args:
        keywords (List[str]): List of keywords to include in the word cloud.
        sentiment_label (str): Sentiment label to generate the word cloud for.

    Returns:
        WordCloud: The generated word cloud.
    """
    logger.info(f"Generating word cloud for {sentiment_label} sentiment.")
    
    try:
        text = " ".join(keywords)
        wordcloud = WordCloud(
            width=800, height=400, background_color="white", colormap="viridis"
        ).generate(text)
        logger.info("Word cloud generated successfully.")
        return wordcloud

    except Exception as e:
        logger.error(f"Error generating word cloud: {e}")
        return WordCloud()  # Return an empty WordCloud in case of an error

# Example usage (uncomment to run):
# if __name__ == "__main__":
#     keywords = ["happy", "joyful", "positive", "light", "bright"]
#     sentiment_label = "Positive"
#     wc = generate_wordcloud(keywords, sentiment_label)
#     plt.imshow(wc, interpolation="bilinear")
#     plt.axis("off")
#     plt.show()
