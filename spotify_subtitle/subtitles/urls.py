from django.urls import path
from .views import SubtitleUploadAPIView, Logout, login, Register, ValidToken, NowPlayingAPIView,\
    SpotifyCallbackView, SpotifyAuthURLView

urlpatterns = [
    path('login/', login),
    path('logout/', Logout.as_view()),
    path('register/', Register.as_view()),
    path('validate-token/', ValidToken.as_view(), name='validate-token'),
    path('generate_spotify_auth_url/', SpotifyAuthURLView.as_view(), name='generate_spotify_auth_url'),
    path('callback/', SpotifyCallbackView.as_view(), name='spotify_callback'),

    path('upload/', SubtitleUploadAPIView.as_view(), name='upload-subtitle'),
    path('subtitle/', NowPlayingAPIView.as_view(), name='subtitle'),
    # path('subtitles/') to do create a view for return list of subtitles that own to user self
]
