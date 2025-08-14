from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from ..services import SpotifyService
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


class SpotifyAuthURLView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        service = SpotifyService(user=request.user)
        auth_url = service.generate_auth_url()
        return JsonResponse({'auth_url': auth_url})


class SpotifyConnectRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        service = SpotifyService(user=request.user)
        auth_url = service.generate_auth_url()
        return redirect(auth_url)


class SpotifyCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        state = request.GET.get('state')

        if not code or not state:
            return JsonResponse({'error': 'Missing code or state'}, status=400)

        try:
            service = SpotifyService()
            service.exchange_code_for_tokens(code, state)
            return JsonResponse({'message': 'Authentication successful'})
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Failed to get access token', 'details': str(e)}, status=400)
