from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User

import requests
import base64
import uuid
from django.conf import settings
from subtitles.models import AccessRefreshToken, UserSpotifyState


class SpotifyService:
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    ACCOUNTS_BASE_URL = 'https://accounts.spotify.com'
    API_BASE_URL = 'https://api.spotify.com'

    def __init__(self, user=None):
        self.user = user

    def _get_client_credentials_header(self):
        client_creds = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
        return f'Basic {base64.b64encode(client_creds.encode()).decode()}'

    def generate_auth_url(self):
        state = str(uuid.uuid4())
        UserSpotifyState.objects.update_or_create(user=self.user, defaults={'state': state})

        scope = "user-read-playback-state user-read-currently-playing user-read-recently-played"
        params = {
            'client_id': settings.SPOTIFY_CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
            'scope': scope,
            'state': state,
        }
        return f"{self.ACCOUNTS_BASE_URL}/authorize?{requests.compat.urlencode(params)}"

    def exchange_code_for_tokens(self, code, state):
        try:
            user_info = UserSpotifyState.objects.get(state=state)
            user = user_info.user
            user_info.delete()
        except UserSpotifyState.DoesNotExist:
            raise ValueError("Invalid state parameter")

        headers = {
            'Authorization': self._get_client_credentials_header(),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        }
        response = requests.post(self.TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()

        token_data = response.json()
        AccessRefreshToken.objects.update_or_create(
            user=user,
            defaults={
                'access_token': token_data.get('access_token'),
                'refresh_token': token_data.get('refresh_token')
            }
        )
        return token_data

    def _refresh_token(self):
        token_record = AccessRefreshToken.objects.get(user=self.user)
        headers = {
            'Authorization': self._get_client_credentials_header(),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': token_record.refresh_token,
        }
        response = requests.post(self.TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()

        token_data = response.json()
        token_record.access_token = token_data['access_token']
        if 'refresh_token' in token_data:
            token_record.refresh_token = token_data['refresh_token']
        token_record.save()
        return token_record.access_token

    def _make_api_request(self, url):
        token_record = AccessRefreshToken.objects.get(user=self.user)
        headers = {'Authorization': f'Bearer {token_record.access_token}'}
        response = requests.get(url, headers=headers)

        if response.status_code == 401:
            new_access_token = self._refresh_token()
            headers['Authorization'] = f'Bearer {new_access_token}'
            response = requests.get(url, headers=headers)

        response.raise_for_status()
        return response

    def get_now_playing_song_id(self):
        song_id = None

        try:
            response = self._make_api_request(f"{self.API_BASE_URL}/v1/me/player/currently-playing")

            if response.status_code == 200:
                data = response.json()
                if data and data.get('item'):
                    song_id = data['item'].get('id')

            if not song_id:
                response = self._make_api_request(f"{self.API_BASE_URL}/v1/me/player/recently-played?limit=1")
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items')
                    if items and len(items) > 0 and items[0].get('track'):
                        song_id = items[0]['track'].get('id')

        except requests.exceptions.RequestException as e:
            print(f"Error making Spotify API request: {e}")
            return None

        return song_id

    def _get_server_access_token(self):
        headers = {
            'Authorization': self._get_client_credentials_header(),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {'grant_type': 'client_credentials'}
        response = requests.post(self.TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        return response.json().get('access_token')

    def get_track_info(self, song_id):
        access_token = self._get_server_access_token()
        if not access_token:
            raise ValueError("Could not retrieve server access token.")

        url = f"{self.API_BASE_URL}/v1/tracks/{song_id}"
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def exchange_code_for_user(self, code, state):
        user_info = UserSpotifyState.objects.get(state=state)
        user_info.delete()

        token_data = self.exchange_code_for_tokens(code, state)
        access_token = token_data.get('access_token')

        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(f"{self.API_BASE_URL}/v1/me", headers=headers)
        response.raise_for_status()
        spotify_data = response.json()

        spotify_id = spotify_data['id']
        email = spotify_data.get('email', f'{spotify_id}@spotify.user')

        try:
            social_account = SocialAccount.objects.get(provider='spotify', uid=spotify_id)
            user = social_account.user
        except SocialAccount.DoesNotExist:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': spotify_id}
            )
            SocialAccount.objects.create(user=user, provider='spotify', uid=spotify_id)

        return user
