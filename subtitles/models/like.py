from django.db import models
from django.contrib.auth.models import User
from .subtitle import Subtitle


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    subtitle = models.ForeignKey(Subtitle, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'subtitle')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} likes {self.subtitle.id}"
