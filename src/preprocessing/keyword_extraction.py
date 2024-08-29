from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from src.utils.logger import setup_logger
import nltk

nltk.download('punkt')
nltk.download('stopwords')

# Setup logger
logger = setup_logger()


def preprocess_text(text):
    logger.info("Preprocessing text for tokenization and stopword removal.")
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    filtered_words = [word for word in words if word.isalnum() and word.lower() not in stop_words]
    logger.info("Text preprocessed successfully.")
    return filtered_words


def extract_keywords(texts, top_n=10):
    logger.info("Starting keyword extraction using TF-IDF.")
    vectorizer = TfidfVectorizer(max_df=0.85, max_features=10000, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
    
    keyword_scores = defaultdict(float)
    
    for row in tfidf_matrix:
        for idx in row.nonzero()[1]:
            keyword_scores[feature_names[idx]] += row[0, idx]
    
    sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
    logger.info("Keyword extraction completed successfully.")
    return [kw[0] for kw in sorted_keywords[:top_n]]


def aggregate_keywords(texts, top_n=10):
    logger.info("Aggregating keywords across all articles.")
    keywords = extract_keywords(texts, top_n)
    logger.info(f"Top {top_n} aggregated keywords: {keywords}")
    return keywords
