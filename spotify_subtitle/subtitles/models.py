from django.db import models
from django.contrib.auth.models import User
from django.db.models import F, Q


class Subtitle(models.Model):
    song_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('song_id', 'user')

    def __str__(self):
        return f"Subtitle for song ID: {self.song_id}"


class Segment(models.Model):
    subtitle = models.ForeignKey(Subtitle, on_delete=models.CASCADE, related_name='segments')
    segment_number = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    text = models.CharField(max_length=512)

    class Meta:
        ordering = ('subtitle', 'segment_number')
        constraints = [
            models.CheckConstraint(
                check=Q(segment_number__gt=0),
                name='segment_number_positive',
            ),
            models.CheckConstraint(
                check=Q(start_time__lt=F('end_time')),
                name='start_before_end',
            ),
            models.UniqueConstraint(
                fields=['subtitle', 'segment_number'],
                name='unique_segment_number_per_subtitle',
            )
        ]

    def __str__(self):
        return f"Text: {self.text}"


class AccessRefreshToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=1024)
    refresh_token = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tokens for {self.user.username}"


class UserSpotifyState(models.Model):
    user_id = models.IntegerField(unique=True)
    state = models.CharField(max_length=256, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user_id} - State {self.state}"
