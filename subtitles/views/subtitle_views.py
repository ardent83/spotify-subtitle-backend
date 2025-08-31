from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema
from ..models import Subtitle
from ..serializers import SubtitleSerializer
from ..services import SubtitleService


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class SubtitleListCreateAPIView(APIView):
    serializer_class = SubtitleSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SubtitleSerializer,
        responses={201: SubtitleSerializer}
    )
    def post(self, request, *args, **kwargs):
        service = SubtitleService()
        try:
            subtitle = service.create_subtitle(request.data, request.user)
            serializer = SubtitleSerializer(subtitle, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SubtitleDetailAPIView(APIView):
    serializer_class = SubtitleSerializer
    permission_classes = [IsAuthenticated]

    def get_object_and_check_perm(self, subtitle_id, user, check_owner=False):
        try:
            subtitle = Subtitle.objects.select_related('user').get(id=subtitle_id)
            if check_owner and subtitle.user != user:
                raise PermissionError("Permission denied.")
            if not subtitle.is_public and subtitle.user != user:
                raise PermissionError("This subtitle is private.")
            return subtitle
        except Subtitle.DoesNotExist:
            return None

    def get(self, request, subtitle_id, *args, **kwargs):
        try:
            subtitle = self.get_object_and_check_perm(subtitle_id, request.user)
            if not subtitle:
                return Response({"error": "Subtitle not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = SubtitleSerializer(subtitle, context={'request': request})
            return Response(serializer.data)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, subtitle_id, *args, **kwargs):
        try:
            subtitle = self.get_object_and_check_perm(subtitle_id, request.user, check_owner=True)
            if not subtitle:
                return Response({"error": "Subtitle not found."}, status=status.HTTP_404_NOT_FOUND)

            service = SubtitleService()
            updated_subtitle = service.update_subtitle(subtitle, request.user, request.data)
            serializer = SubtitleSerializer(updated_subtitle, context={'request': request})
            return Response(serializer.data)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, subtitle_id, *args, **kwargs):
        try:
            subtitle = self.get_object_and_check_perm(subtitle_id, request.user, check_owner=True)
            if not subtitle:
                return Response({"error": "Subtitle not found."}, status=status.HTTP_404_NOT_FOUND)

            service = SubtitleService()
            service.delete_subtitle(subtitle, request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)


class ToggleLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, subtitle_id, *args, **kwargs):
        try:
            subtitle = Subtitle.objects.get(id=subtitle_id)
            service = SubtitleService()
            is_liked, likes_count = service.toggle_like(request.user, subtitle)
            return Response({'is_liked': is_liked, 'likes_count': likes_count})
        except Subtitle.DoesNotExist:
            return Response({"error": "Subtitle not found."}, status=status.HTTP_404_NOT_FOUND)


class LikedSubtitlesListView(APIView):
    serializer_class = SubtitleSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        service = SubtitleService()
        subtitles = service.get_liked_subtitles(request.user)
        serializer = SubtitleSerializer(subtitles, many=True, context={'request': request})
        return Response(serializer.data)


class NowPlayingAPIView(APIView):
    serializer_class = SubtitleSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        song_id = request.GET.get('songId', None)
        if not song_id:
            return Response(data={"success": False, "error": "Song ID is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        subtitle_service = SubtitleService()
        subtitle = None

        if request.user.is_authenticated:
            subtitle = subtitle_service.get_active_subtitle_for_song(request.user, song_id)
            print(f"{request.user}: {subtitle.id}")

        if not subtitle:
            language = request.GET.get('language', "en")
            subtitle = subtitle_service.get_best_public_subtitle(song_id, language)

        if not subtitle:
            return Response(data={"success": False, "error": "No suitable subtitle found for this song."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = SubtitleSerializer(subtitle, context={'request': request})
        return Response(data={"success": True, "subtitle": serializer.data}, status=status.HTTP_200_OK)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 100


class SongSubtitleListView(APIView):
    serializer_class = SubtitleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request, song_id, *args, **kwargs):
        service = SubtitleService()
        filters = {
            'language': request.query_params.get('language', None),
            'by_user': request.query_params.get('by_user', None),
            'sort_by': request.query_params.get('sort_by', 'likes_desc'),
        }
        subtitles_queryset = service.get_available_subtitles_for_song(song_id, request.user, filters)
        paginator = self.pagination_class()
        paginated_subtitles = paginator.paginate_queryset(subtitles_queryset, request, view=self)
        serializer = SubtitleSerializer(paginated_subtitles, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class SetActiveSubtitleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, subtitle_id, *args, **kwargs):
        try:
            subtitle_to_set = Subtitle.objects.get(id=subtitle_id)
            service = SubtitleService()
            service.set_active_subtitle(request.user, subtitle_to_set.song_id, subtitle_to_set)
            print(f"{request.user}: {subtitle_id}")
            return Response({"success": True, "message": "Active subtitle has been set."}, status=status.HTTP_200_OK)
        except Subtitle.DoesNotExist:
            return Response({"error": "Subtitle not found."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)


class GetActiveSubtitleForSongView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, song_id, *args, **kwargs):
        service = SubtitleService()
        active_subtitle = service.get_active_subtitle_for_song(request.user, song_id)
        if not active_subtitle:
            return Response({"error": "No active subtitle set for this song."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubtitleSerializer(active_subtitle, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, song_id, *args, **kwargs):
        service = SubtitleService()
        service.unset_active_subtitle(request.user, song_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
