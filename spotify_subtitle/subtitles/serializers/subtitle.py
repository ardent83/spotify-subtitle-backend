from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from ..models import Subtitle, Segment


class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = ['segment_number', 'start_time', 'end_time', 'text']


class SubtitleSerializer(serializers.ModelSerializer):
    segments = SegmentSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    file = serializers.FileField(write_only=True, required=True, allow_null=False)

    is_liked_by_current_user = serializers.SerializerMethodField()

    class Meta:
        model = Subtitle
        fields = [
            'id', 'title', 'song_id', 'user', 'language', 'language_display',
            'is_public', 'likes_count', 'is_liked_by_current_user',
            'created_at', 'segments', 'file'
        ]
        read_only_fields = ['id', 'user', 'likes_count', 'created_at', 'segments', 'language_display']

    @extend_schema_field(serializers.BooleanField())
    def get_is_liked_by_current_user(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.likes.filter(user=user).exists()
        return False
