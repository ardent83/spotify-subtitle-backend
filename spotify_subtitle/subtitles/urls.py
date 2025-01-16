from django.urls import path
from . import views

urlpatterns = [
    path('add-subtitle/', views.add_subtitle, name='add_subtitle'),
    path('get-subtitle/<str:song_id>/', views.get_subtitles, name='get_subtitles')
]
