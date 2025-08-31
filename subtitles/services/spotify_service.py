import requests
import base64
from django.conf import settings
from django.core.cache import cache


class SpotifyService:
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    API_BASE_URL = 'https://api.spotify.com'
    CACHE_KEY = 'spotify_server_access_token'

    def _get_client_credentials_header(self):
        client_creds = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
        return f'Basic {base64.b64encode(client_creds.encode()).decode()}'

    def _get_server_access_token(self):
        token = cache.get(self.CACHE_KEY)
        if token:
            return token

        headers = {
            'Authorization': self._get_client_credentials_header(),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {'grant_type': 'client_credentials'}
        response = requests.post(self.TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()

        token_data = response.json()
        access_token = token_data.get('access_token')
        expires_in = token_data.get('expires_in', 3600)

        if access_token:
            cache.set(self.CACHE_KEY, access_token, timeout=expires_in - 60)

        return access_token

    def get_track_info(self, song_id):
        access_token = self._get_server_access_token()
        if not access_token:
            raise ValueError("Could not retrieve server access token.")

        url = f"{self.API_BASE_URL}/v1/tracks/{song_id}"
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
