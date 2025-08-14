from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import AccessRefreshToken


class AccessTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRefreshToken
        fields = ['user', 'access_token', 'refresh_token', 'created_at']
