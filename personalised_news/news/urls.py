from django.urls import path
from . import views

urlpatterns = [
    path('api/news/<str:emotion>/', views.get_news_by_emotion, name='news_by_emotion'),
]
