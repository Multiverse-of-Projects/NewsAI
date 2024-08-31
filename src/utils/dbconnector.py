import os

from dotenv import load_dotenv
from pymongo import MongoClient

from src.utils.logger import setup_logger

logger = setup_logger()

# Load environment variables
load_dotenv()


def get_mongo_client():
    """
    Connects to MongoDB and returns the database object.

    Uses environment variables for connection:
        MONGO_USERNAME: username for MongoDB authentication
        MONGO_PASSWORD: password for MongoDB authentication
        MONGO_DB_NAME: name of the database to connect to

    Returns:
        pymongo.database.Database: the connected database object

    Raises:
        Exception: if connection fails
    """
    try:
        mongo_uri = f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@devasy23.a8hxla5.mongodb.net/?retryWrites=true&w=majority&appName=Devasy23"
        db_name = os.getenv("DB_NAME")
        client = MongoClient(mongo_uri, socketTimeoutMS=60000, connectTimeoutMS=60000)
        db = client[db_name]
        logger.info("Successfully connected to MongoDB.")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


def insert_document(collection_name, document):
    """
    Inserts a document into the given collection.

    Args:
        collection_name (str): The name of the collection.
        document (dict): The document to be inserted.

    Returns:
        str: The ID of the inserted document.

    Raises:
        Exception: If there is an error inserting the document.
    """
    db = get_mongo_client()
    collection = db[collection_name]
    try:
        result = collection.insert_one(document)
        logger.info(f"Document inserted with ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        logger.error(f"Failed to insert document: {e}")
        raise


def find_one_document(collection_name, query):
    db = get_mongo_client()
    collection = db[collection_name]
    try:
        result = collection.find_one(query)
        return result
    except Exception as e:
        logger.error(f"Failed to find document: {e}")
        raise


def append_to_document(collection_name, query, update_data):
    """
    Appends new data to an existing document in the MongoDB collection.

    Args:
        collection_name (str): The name of the MongoDB collection.
        query (dict): The query to select the document to update.
        update_data (dict): The new data to be appended to the document.

    Returns:
        int: The number of documents updated.
    """
    db = get_mongo_client()
    collection = db[collection_name]
    try:
        result = collection.update_one(query, {"$set": update_data})
        if result.modified_count > 0:
            logger.info(f"Document updated successfully.")
        else:
            logger.warning(f"No document matched the query. No update performed.")
        return result.modified_count
    except Exception as e:
        logger.error(f"Failed to update document: {e}")
        raise


def find_documents(collection_name, query):
    """
    Finds documents in the given MongoDB collection using the given query.

    Args:
        collection_name (str): The name of the MongoDB collection.
        query (dict): The query to select documents.

    Returns:
        list: A list of documents found by the query.

    Raises:
        Exception: If there is an error finding documents.
    """
    db = get_mongo_client()
    collection = db[collection_name]
    try:
        documents = collection.find(query)
        return documents
    except Exception as e:
        logger.error(f"Failed to find documents: {e}")
        raise
