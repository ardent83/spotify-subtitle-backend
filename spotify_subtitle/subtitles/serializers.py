from rest_framework import serializers
from .models import Subtitle, User, Segment


class SegmentSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(format='%H:%M:%S')
    end_time = serializers.TimeField(format='%H:%M:%S')

    class Meta:
        model = Segment
        fields = ['segment_number', 'start_time', 'end_time', 'text']

    def validate_segment_number(self, value):
        if value <= 0:
            raise serializers.ValidationError("Segment number must be positive.")
        return value


class SubtitleSerializer(serializers.ModelSerializer):
    segments = SegmentSerializer(many=True)

    class Meta:
        model = Subtitle
        fields = ['id', 'song_id', 'user', 'segments', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']
