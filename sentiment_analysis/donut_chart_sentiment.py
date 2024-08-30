import json

import matplotlib.pyplot as plt

# Read data from JSON file
with open('article_sentiment2.json') as file:
    data = json.load(file)

positive_count = 0
negative_count = 0
neutral_count = 0
for article in data:
    if(article["score"] < 0.75 ):
        neutral_count += 1
    elif(article["sentiment"] == "NEGATIVE"):
        negative_count += 1
    elif(article["sentiment"] == "POSITIVE"):
        positive_count += 1

print(positive_count, negative_count, neutral_count)
# Create donut chart
labels = ['Positive', 'Negative', 'Neutral']
sizes = [positive_count, negative_count, neutral_count]
colors = ['#66CC66', '#FF6666', '#999999']
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.4))
plt.axis('equal')

# Add a title
plt.title('Sentiment Analysis')

# Display the chart
plt.show()