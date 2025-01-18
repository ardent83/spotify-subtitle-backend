import os

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Subtitle, Segment
from ..serializers import SubtitleSerializer
from rest_framework.parsers import MultiPartParser, FormParser
import re


class SubtitleUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        print(type(file))
        song_id = request.data.get('song_id')
        print(file, song_id)
        if not file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        if not song_id:
            return Response({"error": "No song ID provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            #must be lock?
            save_path = os.path.join("temp", 'uploaded_subtitle.srt')

            with open(save_path, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            print(f"File saved at: {save_path}")
            with open(save_path, 'r', encoding='utf-8') as saved_file:
                saved_content = saved_file.read()
                print(f"Saved file content: \n{saved_content}")

            segments_data = self.parse_srt(saved_content)

            subtitle = Subtitle.objects.create(
                song_id=song_id,
                user=request.user
            )

            for segment_data in segments_data:
                Segment.objects.create(
                    subtitle=subtitle,
                    segment_number=segment_data['segment_number'],
                    start_time=segment_data['start_time'],
                    end_time=segment_data['end_time'],
                    text=segment_data['text']
                )

            serializer = SubtitleSerializer(subtitle)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except UnicodeDecodeError:
            return Response({"error": "The file encoding is not valid UTF-8."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def parse_srt(self, srt_content):
        segments = []
        if not srt_content:
            raise ValueError("The SRT file is empty.")

        # Regex pattern to parse SRT content
        pattern = re.compile(
            r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n([\s\S]*?)(?=\n\d+\n|\Z)', re.DOTALL
        )

        matches = pattern.findall(srt_content)

        if not matches:
            raise ValueError("The SRT file format is invalid.")

        for match in matches:
            segment_number, start_time, end_time, text = match
            start_time = start_time.replace(',', '.')
            end_time = end_time.replace(',', '.')
            segments.append({
                'segment_number': int(segment_number),
                'start_time': start_time,
                'end_time': end_time,
                'text': text.strip()
            })

        return segments


class SubtitleRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, song_id, *args, **kwargs):
        try:
            subtitle = Subtitle.objects.get(song_id=song_id, user=request.user)
            serializer = SubtitleSerializer(subtitle)
            return Response(data={"success": True, "subtitle": serializer.data}, status=status.HTTP_200_OK)
        except Subtitle.DoesNotExist:
            return Response(data={"success": False, "error": "Subtitle not found or you don't have access."},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(data={"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
