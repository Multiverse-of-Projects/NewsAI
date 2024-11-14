import nltk
from nltk.tokenize import sent_tokenize
from transformers import pipeline

from src.utils.dbconnector import find_documents
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

# Initialize the NLP pipeline for question generation
question_generator = pipeline("text2text-generation", model="valhalla/t5-small-qg-prepend")

def generate_suggested_questions(article_ids):
    """
    Generate suggested questions from the summaries of the given articles.

    Args:
        article_ids (List[str]): List of article IDs to generate questions for.

    Returns:
        List[str]: List of generated questions.
    """
    documents = find_documents("News_Articles", {"id": {"$in": article_ids}})
    summaries = [doc.get("summary", "") for doc in documents]

    questions = []
    for summary in summaries:
        sentences = sent_tokenize(summary)
        for sentence in sentences:
            input_text = f"generate question: {sentence}"
            generated = question_generator(input_text, max_length=50, num_return_sequences=1)
            question = generated[0]["generated_text"]
            questions.append(question)
            logger.info(f"Generated question: {question}")

    return questions
