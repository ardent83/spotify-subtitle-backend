from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ValidSessionView,
    NowPlayingAPIView,
    SpotifyCallbackView,
    SpotifyAuthURLView,
    SongSubtitleListView,
    SetActiveSubtitleView,
    SubtitleListCreateAPIView,
    SubtitleDetailAPIView,
    ToggleLikeView,
    LikedSubtitlesListView,
    SpotifyTrackInfoView,
    GetActiveSubtitleForSongView,
    LanguageListView,
    ExtensionSpotifyCallbackAPIView,
    SpotifyConnectRedirectView
)

urlpatterns = [
    path('auth/login/', LoginView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
    path('auth/register/', RegisterView.as_view()),
    path('auth/valid_session/', ValidSessionView.as_view(), name='valid_session'),

    path('spotify/generate_spotify_auth_url/', SpotifyAuthURLView.as_view(), name='generate_spotify_auth_url'),
    path('spotify/connect', SpotifyConnectRedirectView.as_view(), name='spotify-connect'),
    path('spotify/callback/', SpotifyCallbackView.as_view(), name='spotify_callback'),
    path('spotify/track/<str:song_id>/', SpotifyTrackInfoView.as_view(), name='spotify-track-info'),

    path('subtitles/', SubtitleListCreateAPIView.as_view(), name='subtitle-list-create'),
    path('subtitles/currently-playing/', NowPlayingAPIView.as_view(), name='subtitle'),
    path('subtitles/<int:subtitle_id>/', SubtitleDetailAPIView.as_view(), name='subtitle-detail'),
    path('subtitles/<int:subtitle_id>/like/', ToggleLikeView.as_view(), name='subtitle-toggle-like'),
    path('subtitles/liked/', LikedSubtitlesListView.as_view(), name='liked-subtitles-list'),
    path('subtitles/<int:subtitle_id>/set-active/', SetActiveSubtitleView.as_view(), name='set-active-subtitle'),

    path('songs/<str:song_id>/subtitles/', SongSubtitleListView.as_view(), name='song-subtitle-list'),
    path('songs/<str:song_id>/active-subtitle/', GetActiveSubtitleForSongView.as_view(),
         name='get-active-subtitle-for-song'),

    path('enums/languages/', LanguageListView.as_view(), name='language-list'),

    path('spotify/extension-callback/', ExtensionSpotifyCallbackAPIView.as_view(), name='spotify-extension-callback'),
]
