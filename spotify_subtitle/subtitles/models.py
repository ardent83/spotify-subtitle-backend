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
                check=Q(start_time__lt=F('end_time')),
                name='start_before_end',
            )
        ]

    def __str__(self):
        return f"Text: {self.text}"
