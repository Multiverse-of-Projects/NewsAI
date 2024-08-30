from transformers import pipeline
import json

classifier = pipeline(model="facebook/bart-large-mnli")
candidate_labels = ["general", "finance", "entertainment", "sports", "technology", "politics"]

result = classifier("People in Erode urged to use eco-friendly Vinayaka idols", candidate_labels=candidate_labels)
print(result)
with open("articles.json", "r", encoding="utf-8") as f:
    article_contents = json.load(f)

topic_classified_articles = []

num_true = 0
num_false = 0
match=None

i=0
for article in article_contents:
    print(i)
    i=i+1
    description = article.get("description")
    title = article.get("title")
    category = article.get("category")

    result = classifier(title+description, candidate_labels=candidate_labels)
    if(result.get("labels")[0] == category):
        match = True
        num_true += 1

    else:
        match = False
        num_false += 1
    topic_classified_articles.append({
        "title": title,
        "description": description,
        "topic": result.get("labels")[0],
        "score": result.get("scores")[0],
        "match": match
    })

print(f"Matched: {num_true}, Not Matched: {num_false}")
with open("topic_classified_articles.json", "w", encoding="utf-8") as f:
    json.dump(topic_classified_articles, f, ensure_ascii=False, indent=4)