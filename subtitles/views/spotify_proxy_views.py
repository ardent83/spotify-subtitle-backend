from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import JsonResponse
from ..services import SpotifyService


class SpotifyTrackInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, song_id, *args, **kwargs):
        try:
            service = SpotifyService()
            track_data = service.get_track_info(song_id)
            return JsonResponse(track_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
