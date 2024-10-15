from django.db import models

class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    emotion = models.CharField(max_length=50, choices=[('happy', 'Happy'), ('sad', 'Sad'), ('angry', 'Angry'), ('surprised', 'Surprised')], default='neutral')
