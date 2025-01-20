import requests
import base64
import uuid

from django.conf import settings
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from subtitles.models import AccessRefreshToken, UserSpotifyState, User


class SpotifyCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        state = request.GET.get('state')
        print(state)
        user_info = UserSpotifyState.objects.filter(state=state).first()

        if not user_info:
            return JsonResponse({'error': 'Invalid state parameter'}, status=400)

        user_id = user_info.user_id

        user_info.delete()

        if not code:
            return JsonResponse({'error': 'No code provided'}, status=400)

        token_url = 'https://accounts.spotify.com/api/token'

        client_creds = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
        headers = {
            'Authorization': f'Basic {base64.b64encode(client_creds.encode()).decode()}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        }

        response = requests.post(token_url, data=data, headers=headers)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            refresh_token = token_data.get('refresh_token')

            AccessRefreshToken.objects.update_or_create(
                user=User.objects.get(id=user_id),
                defaults={
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            )

            return JsonResponse({'message': 'Authentication successful', 'access_token': access_token})
        else:
            error_details = response.json() if response.content else {}
            return JsonResponse({'error': 'Failed to get access token', 'details': error_details}, status=400)


class SpotifyAuthURLView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        state = str(uuid.uuid4())
        print(user_id, state)
        UserSpotifyState.objects.filter(user_id=user_id).delete()
        UserSpotifyState.objects.create(user_id=user_id, state=state)

        auth_url = (
            f"https://accounts.spotify.com/authorize?"
            f"client_id={settings.SPOTIFY_CLIENT_ID}"
            f"&response_type=code"
            f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}"
            f"&scope=user-read-playback-state user-read-currently-playing"
            f"&state={state}"
        )

        return JsonResponse({'auth_url': auth_url})
