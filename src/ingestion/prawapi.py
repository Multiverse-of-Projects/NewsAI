import json
import os
import sys
from datetime import datetime

import praw
from dotenv import load_dotenv

from src.utils.logger import setup_logger

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..")))

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

COMMENT_COUNT = 10
TIME_SLOT = "all"


def clean_content(content: str) -> str:
    """
    Clean a string by replacing carriage returns and newlines with spaces and then removing excessive spaces.

    Args:
        content (str): The string to clean.

    Returns:
        str: The cleaned string.
    """
    if not isinstance(content, str):
        raise ValueError("Input must be a string.")
    cleaned_content = content.replace("\r", " ").replace("\n", " ")
    cleaned_content = " ".join(cleaned_content.split())
    return cleaned_content


def fetch_reddit_posts_by_keyword(keyword: str, limit: int = 10, to_json: bool = True):
    """
    Fetches Reddit posts containing the given keyword.

    Args:
        keyword (str): The keyword to search for in Reddit posts.
        limit (int, optional): The number of posts to fetch. Defaults to 10.
        to_json (bool, optional): Whether to store the results in a JSON file. Defaults to True.

    Returns:
        List[Dict]: A list of dictionaries containing the post data.
    """
    try:
        search_results = reddit.subreddit("all").search(
            query=keyword,
            sort="relevance",
            time_filter=TIME_SLOT,
            limit=limit,
        )

        posts = []
        for post in search_results:
            if not post or post.stickied:
                continue

            post_data = {
                "title": post.title,
                "id": post.id,
                "content": clean_content(post.selftext),
                "url": post.url,
                "created_utc": datetime.utcfromtimestamp(post.created_utc).isoformat(),
                "top_comments": [],
            }

            try:
                comments = post.comments.list()
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

            posts.append(post_data)
            logger.debug(f"Post Title: {post.title}")
            logger.debug(f"Post URL: {post.url}")
            logger.debug(f"Post Content: {post.selftext[:100]}")

        if to_json:
            try:
                filename = f"{keyword}_posts_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(posts, f, ensure_ascii=False, indent=4)
                logger.info(f"Results stored in {filename}")
            except Exception as e:
                logger.error(f"Error occurred while storing results: {str(e)}")
        else:
            logger.info(f"Fetched {len(posts)} posts containing the keyword '{keyword}'")

    except Exception as e:
        logger.error(f"Error fetching posts: {type(e).__name__} - {str(e)}")


if __name__ == "__main__":
    fetch_reddit_posts_by_keyword(keyword="python", limit=10)
