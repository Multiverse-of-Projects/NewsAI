import os
from typing import List

import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import HarmBlockThreshold, HarmCategory

from src.utils.dbconnector import append_to_document, find_documents
from src.utils.logger import setup_logger

load_dotenv()

# Configure the Gemini API with the provided API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Setup logger
logger = setup_logger()

def summarize_texts(
    articles_id: List[str], max_length: int = 200, min_length: int = 20
):
    """
    Summarizes a list of texts using a pre-trained Transformer model.

    Args:
        articles_id (List[str]): List of article IDs to summarize.
        max_length (int): Maximum length of the summary.
        min_length (int): Minimum length of the summary.

    Returns:
        List[dict]: List of dictionaries containing article IDs and their summaries.
    """
    texts = []
    logger.info("Initializing summarization pipeline.")
    
    # Retrieve articles from the database
    articles = find_documents("News_Articles", {"id": {"$in": articles_id}})
    for article in articles:
        texts.append(
            {"id": article["id"], "content": article.get("content", "")}
        )
    
    article_summaries = []

    logger.info(f"Starting summarization of {len(texts)} articles.")
    for idx, obj in enumerate(texts):
        logger.debug(f"Summarizing article {idx + 1}/{len(texts)}.")
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
            Summarize the provided news document while preserving the most important keywords and maintaining the original sentiment or tone. Ensure that the summary is concise, accurately reflects the key points, and retains the emotional impact or intent of the original content.

            News Article:
            {obj.get("content")}
            """
            # Generate summary with safety settings
            response = model.generate_content(
                prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                },
            )
            logger.debug(f"Summary generated: {response.text}")
            article_summaries.append(
                {"id": obj.get("id"), "summary": response.text}
            )
            # Append the summary to the document in the database
            append_to_document(
                "News_Articles", {"id": obj.get("id")}, {"summary": response.text}
            )
            logger.debug(f"Summary for article {idx + 1} saved: {response.text}")

        except Exception as e:
            logger.error(f"Error summarizing article {idx + 1}: {e}")
            article_summaries.append({"id": obj.get("id"), "summary": ""})
            append_to_document("News_Articles", {"id": obj.get("id")}, {"summary": ""})

    logger.info("Summarization completed.")
    return article_summaries

if __name__ == "__main__":
    # Test summarization with sample texts
    articles_to_summarize = [
        {
            "id": "1",
            "content": "Early on Friday morning, a 31-year-old female trainee doctor retired to sleep in a seminar hall after a gruelling day at one of India’s oldest hospitals. [...]",
        },
        {
            "id": "2",
            "content": "The rape and murder of a trainee doctor in India’s Kolkata city earlier this month has sparked massive outrage in the country, [...]",
        },
    ]

    # Call the summarize_texts function
    summaries = summarize_texts([article["id"] for article in articles_to_summarize])
    for summary in summaries:
        print(f"Article ID: {summary['id']}\nSummary: {summary['summary']}\n")
