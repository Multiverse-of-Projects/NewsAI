"""
Cleanup script to remove problematic or incomplete articles from the MongoDB database.

This script identifies and optionally removes articles that:
1. Don't have all required fields (content, summary, keywords, sentiment)
2. Have empty or null values for required fields
3. Have specific IDs that you want to remove
"""

import sys
import json
from typing import List, Dict, Optional, Set, Union

from .dbconnector import get_mongo_client, find_documents
from .logger import setup_logger

# Setup logger
logger = setup_logger()

def identify_incomplete_articles(required_fields: List[str] = None) -> List[str]:
    """
    Identify articles that are missing required fields.
    
    Args:
        required_fields (List[str], optional): List of required fields to check. 
                                              Defaults to ['content', 'summary', 'keywords', 'sentiment'].
    
    Returns:
        List[str]: List of article IDs that are missing required fields.
    """
    if required_fields is None:
        required_fields = ['content', 'summary', 'keywords', 'sentiment']
    
    logger.info(f"Checking for articles missing required fields: {required_fields}")
    
    try:
        # Find all articles in the database
        client = get_mongo_client()
        db = client["NewsDB"]
        collection = db["News_Articles"]
        
        # Get all articles
        articles = collection.find({})
        
        incomplete_articles = []
        for article in articles:
            article_id = article.get('id')
            if not article_id:
                continue
                
            for field in required_fields:
                # Check if field is missing or empty
                if field not in article or not article[field]:
                    incomplete_articles.append(article_id)
                    logger.warning(f"Article {article_id} missing required field: {field}")
                    break
        
        logger.info(f"Found {len(incomplete_articles)} incomplete articles")
        return incomplete_articles
    except Exception as e:
        logger.error(f"Error identifying incomplete articles: {e}")
        return []

def remove_articles(article_ids: List[str], dry_run: bool = True) -> int:
    """
    Remove articles from the database.
    
    Args:
        article_ids (List[str]): List of article IDs to remove.
        dry_run (bool, optional): If True, only log articles that would be removed without actually removing them.
                                 Defaults to True.
    
    Returns:
        int: Number of articles removed.
    """
    if not article_ids:
        logger.info("No articles to remove")
        return 0
    
    try:
        client = get_mongo_client()
        db = client["NewsDB"]
        collection = db["News_Articles"]
        
        logger.info(f"Found {len(article_ids)} articles to remove")
        
        if dry_run:
            logger.info("DRY RUN: The following articles would be removed:")
            for article_id in article_ids:
                logger.info(f"  - {article_id}")
            return 0
        
        # Remove articles from MongoDB
        result = collection.delete_many({"id": {"$in": article_ids}})
        deleted_count = result.deleted_count
        
        logger.info(f"Removed {deleted_count} articles from the database")
        
        # Also remove the articles from query results
        query_collection = db["Queries"]
        queries = query_collection.find({})
        
        updates = 0
        for query in queries:
            query_article_ids = query.get('ids', [])
            original_count = len(query_article_ids)
            
            # Remove deleted articles from the query's article list
            query_article_ids = [aid for aid in query_article_ids if aid not in article_ids]
            
            if len(query_article_ids) < original_count:
                # Update the query with the filtered article list
                query_collection.update_one(
                    {"_id": query["_id"]},
                    {"$set": {"ids": query_article_ids}}
                )
                updates += 1
        
        logger.info(f"Updated {updates} query documents to remove references to deleted articles")
        return deleted_count
    
    except Exception as e:
        logger.error(f"Error removing articles: {e}")
        return 0

def cleanup_specific_articles(article_ids: List[str], dry_run: bool = True) -> int:
    """
    Remove specific articles by their IDs.
    
    Args:
        article_ids (List[str]): List of article IDs to remove.
        dry_run (bool, optional): If True, only log articles that would be removed without actually removing them.
                                 Defaults to True.
    
    Returns:
        int: Number of articles removed.
    """
    logger.info(f"Removing {len(article_ids)} specific articles")
    return remove_articles(article_ids, dry_run)

def cleanup_query_articles(query: str, dry_run: bool = True) -> int:
    """
    Remove all articles associated with a specific query.
    
    Args:
        query (str): The query string to match.
        dry_run (bool, optional): If True, only log actions without performing them.
                                 Defaults to True.
    
    Returns:
        int: Number of articles removed.
    """
    try:
        client = get_mongo_client()
        db = client["NewsDB"]
        query_collection = db["Queries"]
        
        # Find the query document
        query_doc = query_collection.find_one({"query": query})
        
        if not query_doc:
            logger.warning(f"No query found matching: {query}")
            return 0
        
        article_ids = query_doc.get('ids', [])
        logger.info(f"Found {len(article_ids)} articles associated with query: {query}")
        
        # Remove the query document if not a dry run
        if not dry_run:
            query_collection.delete_one({"_id": query_doc["_id"]})
            logger.info(f"Removed query document for: {query}")
        
        # Remove all associated articles
        return remove_articles(article_ids, dry_run)
    
    except Exception as e:
        logger.error(f"Error cleaning up query articles: {e}")
        return 0

def main():
    """
    Main function to run the cleanup script.
    
    Usage:
        python -m src.utils.cleanup --check  # Check for incomplete articles
        python -m src.utils.cleanup --remove  # Remove incomplete articles
        python -m src.utils.cleanup --ids article_id1,article_id2  # Remove specific articles
        python -m src.utils.cleanup --query "Query String"  # Remove articles for a query
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Cleanup script for removing problematic articles')
    parser.add_argument('--check', action='store_true', help='Check for incomplete articles without removing them')
    parser.add_argument('--remove', action='store_true', help='Remove incomplete articles')
    parser.add_argument('--ids', type=str, help='Comma-separated list of article IDs to remove')
    parser.add_argument('--query', type=str, help='Remove all articles associated with this query')
    
    args = parser.parse_args()
    
    if args.check:
        incomplete_ids = identify_incomplete_articles()
        print(f"Found {len(incomplete_ids)} incomplete articles:")
        for article_id in incomplete_ids:
            print(f"  - {article_id}")
    
    elif args.remove:
        incomplete_ids = identify_incomplete_articles()
        removed = remove_articles(incomplete_ids, dry_run=False)
        print(f"Removed {removed} incomplete articles")
    
    elif args.ids:
        article_ids = args.ids.split(',')
        article_ids = [article_id.strip() for article_id in article_ids]
        removed = cleanup_specific_articles(article_ids, dry_run=False)
        print(f"Removed {removed} specified articles")
    
    elif args.query:
        removed = cleanup_query_articles(args.query, dry_run=False)
        print(f"Removed {removed} articles associated with query: {args.query}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()