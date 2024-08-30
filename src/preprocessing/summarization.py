from transformers import pipeline
from typing import List
from src.utils.logger import setup_logger
# Setup logger
logger = setup_logger()

def summarize_texts(texts: List[str], max_length: int = 150, min_length: int = 50) -> List[str]:
    """
    Summarizes a list of texts using a pre-trained Transformer model.
    
    Args:
        texts (List[str]): List of texts to summarize.
        max_length (int): Maximum length of the summary.
        min_length (int): Minimum length of the summary.
    
    Returns:
        List[str]: List of summarized texts.
    """
    logger.info("Initializing summarization pipeline.")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", tokenizer="facebook/bart-large-cnn")
    
    summaries = []
    logger.info(f"Starting summarization of {len(texts)} texts.")
    for idx, text in enumerate(texts):
        logger.debug(f"Summarizing text {idx+1}/{len(texts)}.")
        try:
            summary = summarizer(
                text, 
                max_length=max_length, 
                min_length=min_length, 
                do_sample=False
            )
            summaries.append(summary[0]['summary_text'])
            logger.debug(f"Summary {idx+1}: {summary[0]['summary_text']}")
        except Exception as e:
            logger.error(f"Error summarizing text {idx+1}: {e}")
            summaries.append("")
    logger.info("Summarization completed.")
    return summaries
