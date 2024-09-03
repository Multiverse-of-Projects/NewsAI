import json
import os
import sys
from datetime import datetime

import praw
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Import setup_logger from utils
from src.utils.logger import setup_logger
from src.utils.dbconnector import insert_document

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENTID"),
    client_secret=os.getenv("REDDIT_SECRETKEY"),
    user_agent="{0} by u/{1}".format(
        os.getenv("REDDIT_APPNAME"), os.getenv("REDDIT_USERNAME")
    ),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
)

logger = setup_logger()

# constants
COMMENT_COUNT = 10
TIME_SLOT = "all"  # Time filter can be 'all', 'day', 'week', 'month', 'year'


def clean_content(content):
    # Replace carriage returns and newlines with spaces
    cleaned_content = content.replace("\r", " ").replace("\n", " ")
    # remove emoji from post content and comment content
    cleaned_content = ''.join(c for c in cleaned_content if c.isascii() and c not in u"\U00010000-\U0010FFFF")
    # Remove excessive spaces (multiple spaces turned into a single space)
    cleaned_content = " ".join(cleaned_content.split())
    return cleaned_content


def fetch_reddit_posts_by_keyword(keyword, limit=10, to_json=True):
    try:
        # Search for posts containing the keyword
        search_results = reddit.subreddit("all").search(
            query=keyword,
            sort="relevance",  # Sort results by relevance
            time_filter=TIME_SLOT,
            limit=limit,
        )

        posts = []
        for post in search_results:
            if not post or post.stickied:  # Skip if post is None or stickied
                continue

            post_data = {
                "title": post.title,
                "id": post.id,
                "content": clean_content(post.selftext),
                "url": post.url,
                "created_utc": datetime.utcfromtimestamp(post.created_utc).isoformat(),
                "discussion_topic": keyword,
                "top_comments": [],
            }

            # Fetch and process top comments
            try:
                comments = post.comments.list()  # Get all comments
                sorted_comments = sorted(
                    comments,
                    key=lambda c: c.score if hasattr(c, "score") else 0,
                    reverse=True,
                )
                top_comments = sorted_comments[:COMMENT_COUNT]

                post_data["top_comments"] = [
                    {
                        "comment_id": comment.id,
                        "comment_content": clean_content(comment.body),
                        "comment_score": comment.score,
                        "comment_created_utc": datetime.utcfromtimestamp(
                            comment.created_utc
                        ).isoformat(),
                    }
                    for comment in top_comments
                    if hasattr(comment, "body")
                ]
            except Exception as e:
                logger.error(f"Error fetching comments for post ID {post.id}: {str(e)}")

            try:
                insert_document('reddit_posts', post_data)  # Replace 'reddit_posts' with your desired collection name
                logger.info(f"Inserted post ID {post.id} into MongoDB")
            except Exception as e:
                logger.error(f"Error inserting post ID {post.id} into MongoDB: {str(e)}")

            # posts.append(post_data)
            logger.debug(f"Post Title: {post.title} Saved to MongoDB")

    except Exception as e:
        logger.error(f"Error fetching posts: {type(e).__name__} - {str(e)}")


if __name__ == "__main__":
    # Example usage: searching for posts about "python"
    fetch_reddit_posts_by_keyword(keyword="python", limit=5)
