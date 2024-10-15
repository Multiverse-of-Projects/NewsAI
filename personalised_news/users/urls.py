from django.urls import path
from . import views

urlpatterns = [
    path('save_preferences/', views.save_preferences, name='save_preferences'),  # Route for saving preferences
    path('get_preferences/', views.get_preferences, name='get_preferences'),  # Route for retrieving preferences
]
