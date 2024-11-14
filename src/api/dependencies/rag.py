import os
from typing import List, Dict

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from transformers import pipeline

from src.utils.dbconnector import find_documents
from src.utils.logger import setup_logger

load_dotenv()

# Setup logger
logger = setup_logger()

# Initialize ChromaDB client
chroma_client = chromadb.Client(
    Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="chroma_db"
    )
)

# Initialize embedding function
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Create or get collection
collection = chroma_client.get_or_create_collection(
    name="news_summaries",
    embedding_function=embedding_function
)

# Initialize the LLM pipeline
llm_pipeline = pipeline("text-generation", model="gpt-3.5-turbo")

def store_embeddings(article_ids: List[str]):
    """
    Store embeddings of the article summaries in ChromaDB.

    Args:
        article_ids (List[str]): List of article IDs to store embeddings for.
    """
    documents = find_documents("News_Articles", {"id": {"$in": article_ids}})
    for doc in documents:
        summary = doc.get("summary", "")
        if summary:
            collection.add(
                documents=[summary],
                metadatas=[{"id": doc["id"]}],
                ids=[doc["id"]]
            )
            logger.info(f"Stored embedding for article {doc['id']}")

def retrieve_relevant_context(query: str) -> List[str]:
    """
    Retrieve relevant context from the stored embeddings based on the query.

    Args:
        query (str): The query to search for relevant context.

    Returns:
        List[str]: List of relevant contexts.
    """
    results = collection.query(
        query_texts=[query],
        n_results=5
    )
    contexts = [result["document"] for result in results["documents"]]
    return contexts

def generate_answer(query: str, context: List[str]) -> str:
    """
    Generate an answer based on the query and retrieved context.

    Args:
        query (str): The query to generate an answer for.
        context (List[str]): The retrieved context to use for generating the answer.

    Returns:
        str: The generated answer.
    """
    prompt = f"Context: {' '.join(context)}\n\nQuestion: {query}\nAnswer:"
    response = llm_pipeline(prompt, max_length=200, num_return_sequences=1)
    answer = response[0]["generated_text"]
    return answer

def rag_pipeline(query: str) -> str:
    """
    The RAG pipeline to retrieve and generate answers based on the query.

    Args:
        query (str): The query to process.

    Returns:
        str: The generated answer.
    """
    context = retrieve_relevant_context(query)
    answer = generate_answer(query, context)
    return answer
