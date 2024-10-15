from .models import NewsArticle
from sentiment.sentiment_analysis import analyze_emotion
from django.http import JsonResponse

def save_article(title, content):
    # Analyze the emotion of the content
    emotion = analyze_emotion(content)
    new_article = NewsArticle.objects.create(title=title, content=content, emotion=emotion)
    new_article.save()


def get_news_by_emotion(request, emotion):
    articles = NewsArticle.objects.filter(emotion=emotion)
    response_data = [{'title': article.title, 'content': article.content} for article in articles]
    return JsonResponse(response_data, safe=False)
