from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.auth import UserSerializer
from ..models import AccessRefreshToken


@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            django_login(request, user)
            return Response(data={"message": f"Welcome {user.username}!"}, status=status.HTTP_200_OK)
        return Response(data={"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        username = request.user.username
        django_logout(request)
        return Response(data={"message": f"Bye {username}!"}, status=status.HTTP_204_NO_CONTENT)


class ValidSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        has_spotify_token = AccessRefreshToken.objects.filter(user=user).exists()

        return Response({
            "user": user.username,
            "has_spotify_token": has_spotify_token
        })


class RegisterView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        django_login(request, user)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
