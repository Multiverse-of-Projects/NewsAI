import json
import matplotlib.pyplot as plt
from datetime import datetime

# Load data from JSON file
with open('article_sentiment2.json', 'r') as file:
    data = json.load(file)

# Initialize an empty dictionary for sentiment counts by datetime
sentiment_counts_by_datetime = {}

# Process each article
for article in data:
    published_at = article.get("published_at")
    sentiment = article.get("sentiment", "").lower()  # Ensure the sentiment is in lowercase
    
    # Parse the date and hour
    date_hour = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%S%z").replace(minute=0, second=0, tzinfo=None)
    
    # Initialize the dictionary entry if it doesn't exist
    if date_hour not in sentiment_counts_by_datetime:
        sentiment_counts_by_datetime[date_hour] = {'positive': 0, 'negative': 0, 'neutral': 0}
    
    # Increment the appropriate sentiment count for the given date and hour
    if sentiment == "positive":
        sentiment_counts_by_datetime[date_hour]['positive'] += 1
    elif sentiment == "negative":
        sentiment_counts_by_datetime[date_hour]['negative'] += 1
    elif sentiment == "neutral":
        sentiment_counts_by_datetime[date_hour]['neutral'] += 1

# Sort the datetime keys
sorted_datetimes = sorted(sentiment_counts_by_datetime.keys())

# Prepare lists for plotting
positive_counts = [sentiment_counts_by_datetime[dt]['positive'] for dt in sorted_datetimes]
negative_counts = [sentiment_counts_by_datetime[dt]['negative'] for dt in sorted_datetimes]
neutral_counts = [sentiment_counts_by_datetime[dt]['neutral'] for dt in sorted_datetimes]

# Plotting the data
plt.figure(figsize=(12, 6))
plt.plot(sorted_datetimes, positive_counts, label='Positive', color='green', marker='o')
plt.plot(sorted_datetimes, negative_counts, label='Negative', color='red', marker='o')
plt.plot(sorted_datetimes, neutral_counts, label='Neutral', color='gray', marker='o')

# Formatting the plot
plt.xlabel('Datetime (Date and Hour)')
plt.ylabel('Number of Articles')
plt.title('Sentiment Analysis Over Time (by Hour)')
plt.legend()
plt.grid(True)

# Rotate datetime labels on the x-axis for better readability
plt.xticks(rotation=45)

# Show the plot
plt.tight_layout()
plt.show()
