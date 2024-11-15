import os, sys
import unittest
from unittest import TestCase, mock
from unittest.mock import patch, MagicMock
from bson import ObjectId
import mongomock
import pandas as pd
import cProfile
import io
import pstats
srcpath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(srcpath)
from utils.dbconnector import get_mongo_client, MongoDBClientSingleton

# Importované funkcie, ktoré chcete testovať
from utils.dbconnector import (
    get_mongo_client,
    content_manager,
    insert_document,
    find_one_document,
    append_to_document,
    find_documents,
    fetch_and_combine_articles
)

class MongoDBUtilsTests(unittest.TestCase):

    def run_with_profiling(self, test_func):
        """Helper method to profile a single test function."""
        profiler = cProfile.Profile()
        profiler.enable()

        # Run the test
        test_func()

        profiler.disable()
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
        ps.print_stats()
        print(f"\nProfiling results for {test_func.__name__}:\n{s.getvalue()}")
        
    @mock.patch.dict(os.environ, {"TESTING": "true", "MONGO_DB_NAME": "test_db"})
    def test_get_mongo_client_success(self):
        db = get_mongo_client()
        self.assertIsNotNone(db)

    @patch("src.utils.dbconnector.MongoClient")
    def test_get_mongo_client_failure(self, mock_mongo_client):
        # Simulujeme chybu pripojenia
        mock_mongo_client.side_effect = Exception("Connection failed")
        
        with self.assertRaises(Exception) as context:
            get_mongo_client()
        self.assertIn("Connection failed", str(context.exception))

    @patch("utils.dbconnector.get_mongo_client")
    def test_content_manager(self, mock_get_mongo_client):
        mock_db = mongomock.MongoClient().db
        mock_get_mongo_client.return_value = mock_db
        mock_db["News_Articles"].insert_one({
            "id": "article123",
            "content": "Sample content",
            "summary": "Sample summary"
        })

        result = content_manager("article123", ["content", "summary", "keywords"])
        expected_result = {"content": True, "summary": True, "keywords": False}
        self.assertEqual(result, expected_result)

    @patch("utils.dbconnector.get_mongo_client")
    def test_insert_document(self, mock_get_mongo_client):
        mock_db = mongomock.MongoClient().db
        mock_get_mongo_client.return_value = mock_db

        document = {"title": "Test Title", "content": "Test Content"}
        doc_id = insert_document("TestCollection", document)
        self.assertTrue(isinstance(doc_id, ObjectId))

    @patch("utils.dbconnector.get_mongo_client")
    def test_find_one_document(self, mock_get_mongo_client):
        mock_db = mongomock.MongoClient().db
        mock_get_mongo_client.return_value = mock_db
        mock_db["TestCollection"].insert_one({"title": "Test Title"})

        result = find_one_document("TestCollection", {"title": "Test Title"})
        self.assertEqual(result["title"], "Test Title")

    @patch("utils.dbconnector.get_mongo_client")
    def test_append_to_document(self, mock_get_mongo_client):
        mock_db = mongomock.MongoClient().db
        mock_get_mongo_client.return_value = mock_db
        collection = mock_db["TestCollection"]
        collection.insert_one({"title": "Original Title"})

        modified_count = append_to_document(
            "TestCollection", {"title": "Original Title"}, {"title": "Updated Title"}
        )
        self.assertEqual(modified_count, 1)
        updated_doc = collection.find_one({"title": "Updated Title"})
        self.assertIsNotNone(updated_doc)

    @patch("utils.dbconnector.get_mongo_client")
    def test_find_documents(self, mock_get_mongo_client):
        mock_db = mongomock.MongoClient().db
        mock_get_mongo_client.return_value = mock_db
        collection = mock_db["TestCollection"]
        collection.insert_many([{"title": "Title 1"}, {"title": "Title 2"}])

        results = list(find_documents("TestCollection", {}))
        self.assertEqual(len(results), 2)

    @patch("utils.dbconnector.get_mongo_client")
    def test_fetch_and_combine_articles(self, mock_get_mongo_client):
        mock_db = mongomock.MongoClient().db
        mock_get_mongo_client.return_value = mock_db
        collection = mock_db["TestCollection"]
        collection.insert_many([
            {"id": "1", "title": "Article 1", "content": "Content 1"},
            {"id": "2", "title": "Article 2", "content": "Content 2"}
        ])

        df = fetch_and_combine_articles("TestCollection", ["1", "2"])
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn("title", df.columns)
        self.assertIn("content", df.columns)

if __name__ == "__main__":
    unittest.main()  