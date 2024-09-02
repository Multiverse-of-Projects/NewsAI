from src.utils.logger import setup_logger
import json
import os
import sys
from datetime import datetime

import praw
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..")))

# Import setup_logger from utils

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
    # cleaning the content
    cleaned_content = content.replace("\r", " ").replace("\n", " ")
    cleaned_content = content.replace("’", "'")
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
                logger.error(
                    f"Error fetching comments for post ID {post.id}: {str(e)}")

            posts.append(post_data)
            logger.debug(f"Post Title: {post.title}")
            logger.debug(f"Post URL: {post.url}")
            logger.debug(
                f"Post Content: {post.selftext[:100]}"
            )  # Print a snippet of content

        if to_json:
            try:
                filename = os.path.join(
                    os.path.abspath(
                        os.path.join(os.path.dirname(__file__), "..", "..")
                    ),
                    f"{keyword}_posts_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json",
                )
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(posts, f, ensure_ascii=False, indent=4)
                logger.info(f"Results stored in {filename}")
            except Exception as e:
                logger.error(f"Error occurred while storing results: {str(e)}")
        else:
            logger.info(
                f"Fetched {len(posts)} posts containing the keyword '{keyword}'"
            )

        return filename

    except Exception as e:
        logger.error(f"Error fetching posts: {type(e).__name__} - {str(e)}")


if __name__ == "__main__":
    # Example usage: searching for posts about "python"
    fetch_reddit_posts_by_keyword(keyword="gtav", limit=10)
