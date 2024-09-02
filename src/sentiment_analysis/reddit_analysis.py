from src.utils.logger import setup_logger
import json
import os
import sys

import google.generativeai as genai

# importing wordcloud
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..")))

logger = setup_logger()

# def configure_model():
#     # Configure Gemini AI with the API key
#     genai.configure(api_key=os.getenv("GEMINI_AI_API_TOKEN"))

#     # Initialize the GenerativeModel with the specific model name
#     model = genai.GenerativeModel(model_name="gemini-1.5-flash")

#     return model


def summarize_content(content):
    """
    This function takes a string of content as a parameter and summarizes it using the OpenAI API.
    """
    # Configure OpenAI with the API key
    genai.configure(api_key=os.getenv("GEMINI_AI_API_TOKEN"))

    # Initialize the GenerativeModel with the specific model name
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    genai.configure(
        api_key=os.getenv(
            "OPENAI_API_KEY") or "AIzaSyBE62xwU0A0HaaAUesOglJZmLWDeSdlSxQ"
    )

    # Initialize the GenerativeModel with the specific model name
    prompt = (
        "Summarize the following content and reduce the redundancy of the text./n/n"
        f"{content}"
    )

    # Generate a response from the model using the created prompt
    response = model.generate_content(prompt)

    # Process the response (assuming it's in text format)
    # print(response.to_dict())
    return response.text


def sentiment_analysis(content, all_comments):
    """
    This function takes a list of all comments for a single topic as a parameter and analyzes the sentiment of the users for the topic based on the comments.
    """
    genai.configure(api_key=os.getenv("GEMINI_AI_API_TOKEN"))

    # Initialize the GenerativeModel with the specific model name
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={"response_mime_type": "application/json"},
    )
    backslash_char = "\\"
    # Create a prompt to instruct the model to analyze sentiment
    prompt = (
        "Analyze the sentiment of the following comments. "
        "Classify each comment as Positive, Negative, or Neutral based on the overall sentiment expressed in the text."
        "for reference here is the content of the post:"
        f"{content}{backslash_char}n{backslash_char}n"
        "Comments:{backslash_char}n"
        f"{'{backslash_char}n'.join(all_comments)}{backslash_char}n{backslash_char}n"
        "Sentiment Analysis Results:"
    )

    # Generate a response from the model using the created prompt
    response = model.generate_content(prompt)

    # print(response.text)
    # Process the response (assuming it's in text format)
    # print("\nsentiment", response.to_dict())
    # return response.to_dict()

    data = json.loads(response.text)

    # Extract the text content
    # text_content = data['candidates'][0]['content']['parts'][0]['text']

    # Initialize counters
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    positive_count = 0
    negative_count = 0
    neutral_count = 0

    # Count the occurrences of each sentiment
    for _, sentiment in data.items():
        if sentiment == "Positive":
            positive_count += 1
        elif sentiment == "Negative":
            negative_count += 1
        elif sentiment == "Neutral":
            neutral_count += 1
    result = {
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
    }
    return result


if __name__ == "__main__":
    content = None
    comments = None

    with open("concatenated_content.json", "r", encoding="utf-8") as f:
        content = f.read()

    with open("all_comments.json", "r", encoding="utf-8") as f:
        comments = json.load(f)

    # Analyze sentiment for each comment
    content = summarize_content(content)
    sentiment = sentiment_analysis(content, comments)
