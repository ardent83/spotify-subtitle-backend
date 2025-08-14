from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from ..services import SpotifyService
from django.contrib.auth import login


class ExtensionSpotifyCallbackAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        code = request.data.get('code')
        state = request.data.get('state')

        if not code or not state:
            return JsonResponse({'error': 'Missing code or state'}, status=400)

        try:
            service = SpotifyService()
            user = service.exchange_code_for_user(code, state)
            login(request, user)
            return JsonResponse({'success': True, 'username': user.username})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
