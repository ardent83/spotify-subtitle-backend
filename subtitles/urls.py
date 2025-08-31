from django.urls import path
from .views import (
    NowPlayingAPIView,
    SongSubtitleListView,
    SetActiveSubtitleView,
    SubtitleListCreateAPIView,
    SubtitleDetailAPIView,
    ToggleLikeView,
    LikedSubtitlesListView,
    SpotifyTrackInfoView,
    GetActiveSubtitleForSongView,
    LanguageListView,
)

urlpatterns = [
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
]
