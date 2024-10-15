from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_emotions = models.JSONField(default=list)  # Store emotions like ['happy', 'sad']
