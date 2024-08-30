from transformers import pipeline
import json

classifier = pipeline("sentiment-analysis")

def analyze_sentiment(article_content):
    preds = classifier(article_content)
    return preds[0].get("label"), preds[0].get("score")

# Load the article content from article_content.json
with open("article_content.json", "r", encoding="utf-8") as f:
    article_contents = json.load(f)

# Prepare a list to hold the sentiment analysis results
article_sentiments = []

# i=0
# Iterate over each article and analyze its sentiment
for article in article_contents:
    # i = i+1
    # if i > 10:
    #     break
    article_id = article.get("id")
    title = article.get("title")
    description = article.get("description")
    article_content = article.get("article_content")
    published_at = article.get("published_at")

    # Perform sentiment analysis either on the title or description (max size 512)
    sentiment, score = analyze_sentiment(description)

    # Create a new object with the required fields
    sentiment_obj = {
        "id": article_id,
        "title": title,
        "description": description,
        "sentiment": sentiment,
        "score": score,
        "published_at": published_at
    }

    # Add the new object to the list
    article_sentiments.append(sentiment_obj)

# Save the sentiment analysis results to article_sentiment.json
with open("article_sentiment2.json", "w", encoding="utf-8") as f:
    json.dump(article_sentiments, f, ensure_ascii=False, indent=4)

print("Article sentiments have been successfully saved to article_sentiment.json")