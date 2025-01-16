from rest_framework import serializers
from .models import Subtitle, User


class SubtitleSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Subtitle
        fields = ['song_id', 'subtitle_text', 'user', 'created_at']
