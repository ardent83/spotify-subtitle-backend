from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Subtitle
from .serializers import SubtitleSerializer


@api_view('POST')
def add_subtitle(request):
    serializer = SubtitleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_subtitles(request, song_id):
    subtitles = Subtitle.objects.filter(song_id=song_id)
    serializer = SubtitleSerializer(subtitles, many=True)
    return Response(serializer.data)
