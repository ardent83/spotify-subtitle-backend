from django.urls import path
from .views import SubtitleUploadAPIView, Logout, login, Register, ValidToken, SubtitleRetrieveAPIView

urlpatterns = [
    path('login/', login),
    path('logout/', Logout.as_view()),
    path('register/', Register.as_view()),
    path('validate-token/', ValidToken.as_view(), name='validate-token'),

    path('upload/', SubtitleUploadAPIView.as_view(), name='upload-subtitle'),
    path('subtitle/<str:song_id>/', SubtitleRetrieveAPIView.as_view(), name='subtitle'),
    # path('subtitles/') create a view for return list of subtitles that own to user self
]
