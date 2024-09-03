import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.utils.dbconnector import find_documents


def fetch_required_reddit_posts(keyword):
    """
    Fetches the records from mongodb collection for the given keyword

    Args:
        keyword (str): The keyword to search for

    Returns:
        list: A list of documents
    """
    posts = find_documents("reddit_posts", {"discussion_topic":keyword})
    return posts

def extract_post_content(posts):
    """
    First it concate the content of each post
    then it reduces the redunduncy from the content

    Args:
        posts (list): A list of posts
    """
    content = ""
    for post in posts:
        content += post["content"].strip()
        content += " "

    return content
    
def sentiment_analysis(text):
    pass

if __name__ == "__main__":
    posts = fetch_required_reddit_posts(keyword="python")

    # for post in posts:
    #     print(post["title"])
    