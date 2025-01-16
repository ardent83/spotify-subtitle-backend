from django.db import models
from django.contrib.auth.models import User


class Subtitle(models.Model):
    song_id = models.CharField(max_length=255, unique=True)
    subtitle_text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subtitle for song ID: {self.song_id}"
