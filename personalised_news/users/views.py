from django.shortcuts import render
from django.http import JsonResponse
from .models import UserPreferences
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@login_required  # Ensure the user is authenticated
@require_http_methods(["POST"])  # Allow only POST requests for saving preferences
def save_preferences(request):
    preferred_emotions = request.POST.get('preferred_emotions', '')  # Get the preferred emotions from the request
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    user_preferences.preferred_emotions = preferred_emotions  # Save the preferred emotions
    user_preferences.save()
    return JsonResponse({'message': 'Preferences saved successfully'}, status=200)

@login_required  # Ensure the user is authenticated
@require_http_methods(["GET"])  # Allow only GET requests for retrieving preferences
def get_preferences(request):
    user_preferences = UserPreferences.objects.filter(user=request.user).first()  # Get preferences for the logged-in user
    if user_preferences:
        return JsonResponse({'preferred_emotions': user_preferences.preferred_emotions}, status=200)
    return JsonResponse({'message': 'No preferences found'}, status=404)
