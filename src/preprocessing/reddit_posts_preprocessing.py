from src.sentiment_analysis.wordcloud import generate_wordcloud
import json
import os
import re
import sys

import emoji

# importing wordcloud
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..")))


# Function to remove emojis from text
def remove_emojis(text):
    return emoji.replace_emoji(text, replace="")


def remove_escape_characters(s):
    # Define a regex pattern to match escape sequences
    escape_patterns = [
        r"\\n",  # Newline
        r"\\t",  # Tab
        r"\\r",  # Carriage return
        r"\\b",  # Backspace
        r"\\f",  # Form feed
        r"\\\'",  # Single quote
        r"\\\"",  # Double quote
        r"\\\\",  # Backslash
    ]

    # Replace each escape sequence with an empty string
    for pattern in escape_patterns:
        s = re.sub(pattern, "", s)

    return s


def process_reddit_data(json_file_path):
    """
    Processes the Reddit JSON data from the specified file.

    Args:
        json_file_path (str): Path to the JSON file containing Reddit posts.

    Returns:
        tuple: A tuple containing:
            - concatenated_content (str): All post content concatenated into a single string with emojis removed.
            - all_comments (list of str): List of all comments with emojis removed.
    """
    # Read the JSON data from the file
    with open(json_file_path, "r", encoding="utf-8") as file:
        reddit_data = json.load(file)

    # Initialize variables to store concatenated content and comments list
    concatenated_content = ""
    all_comments = []

    # Iterate through each post in the Reddit data
    for post in reddit_data:
        # Remove emojis from post content and concatenate
        content_without_emojis = remove_emojis(post["content"])
        content_escaped_char = remove_escape_characters(content_without_emojis)
        concatenated_content += content_escaped_char + " "

        # Iterate through each comment in the post's top comments
        for comment in post["top_comments"]:
            # Remove emojis from comment content and add to the list
            comment_without_emojis = remove_emojis(comment["comment_content"])
            comment_escaped_char = remove_escape_characters(
                comment_without_emojis)
            all_comments.append(comment_escaped_char)

    # Strip any excess spaces from the concatenated content
    concatenated_content = concatenated_content.strip()

    return concatenated_content, all_comments


if __name__ == "__main__":
    # Specify the path to your JSON file
    json_file_path = "bumble_posts_2024-08-31_10-16-48.json"

    # Call the function and get the results
    concatenated_content, all_comments = process_reddit_data(json_file_path)

    # Output results
    # print("Concatenated Content:")
    # print(concatenated_content)
    # print("\nList of All Comments:")
    # print(all_comments)
    with open("concatenated_content.json", "w", encoding="utf-8") as f:
        json.dump(concatenated_content, f)
    with open("all_comments.json", "w", encoding="utf-8") as f:
        json.dump(all_comments, f)
    # generate the wordcloud removing bumble keyword
    # generate_wordcloud([word for word in concatenated_content.split(" ") if word.lower().strip() != "bumble"], "Positive")
