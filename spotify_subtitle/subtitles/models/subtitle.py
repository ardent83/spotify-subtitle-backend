from django.db import models
from django.contrib.auth.models import User
from django.db.models import F, Q
from ..enums import LANGUAGE_CHOICES


class Subtitle(models.Model):
    song_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subtitles')
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    is_public = models.BooleanField(default=True)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subtitle for {self.song_id} by {self.user.username} [{self.get_language_display()}]"


class Segment(models.Model):
    subtitle = models.ForeignKey(Subtitle, on_delete=models.CASCADE, related_name='segments')
    segment_number = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    text = models.CharField(max_length=512)

    class Meta:
        ordering = ['segment_number']
        constraints = [
            models.UniqueConstraint(fields=['subtitle', 'segment_number'], name='unique_segment_per_subtitle')
        ]

    def __str__(self):
        return f"Segment {self.segment_number} for {self.subtitle.id}"


class UserActiveSubtitle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='active_subtitles')
    song_id = models.CharField(max_length=255)
    active_subtitle = models.ForeignKey(Subtitle, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'song_id')

    def __str__(self):
        return f"{self.user.username}'s active subtitle for {self.song_id} is {self.active_subtitle.id}"
