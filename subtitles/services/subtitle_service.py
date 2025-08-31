import re
from django.db import transaction
from django.db.models import Q
from ..models import Subtitle, Segment, Like, UserActiveSubtitle
from datetime import datetime, timedelta
from ..utils import generate_srt_from_text

MAX_FILE_SIZE_MB = 3
MAX_TEXT_INPUT_CHARS = 10000


class SubtitleService:

    def _parse_srt(self, srt_content):
        srt_content = srt_content.replace('\r\n', '\n').strip()
        segments_data = []
        pattern = re.compile(
            r'(\d+)\n(\d{2}:\d{2}:\d{2}[,.]\d{3}) --> (\d{2}:\d{2}:\d{2}[,.]\d{3})\n([\s\S]*?)(?=\n\n|\Z)', re.DOTALL
        )
        matches = pattern.findall(srt_content)
        if not matches:
            raise ValueError("Invalid SRT file format.")
        for match in matches:
            segment_number, start_time, end_time, text = match
            segments_data.append({
                'segment_number': int(segment_number),
                'start_time': start_time.replace(',', '.'),
                'end_time': end_time.replace(',', '.'),
                'text': text.strip()
            })
        return segments_data

    def _parse_lrc(self, lrc_content):
        lrc_content = lrc_content.replace('\r\n', '\n').strip()
        timestamp_pattern = re.compile(r'\[(\d{2}):(\d{2})\.(\d{2,3})\]')
        all_timed_lines = []

        for line in lrc_content.split('\n'):
            timestamps = timestamp_pattern.findall(line)
            text = timestamp_pattern.sub('', line).strip()

            if timestamps and text:
                for ts in timestamps:
                    minutes, seconds, hundredths = ts
                    start_td = timedelta(minutes=int(minutes), seconds=int(seconds),
                                         milliseconds=int(hundredths.ljust(3, '0')))
                    all_timed_lines.append({'start_timedelta': start_td, 'text': text})

        if not all_timed_lines:
            raise ValueError("Invalid LRC file format or no timed lines found.")

        all_timed_lines.sort(key=lambda x: x['start_timedelta'])

        segments_data = []
        for i, line_data in enumerate(all_timed_lines):
            start_timedelta = line_data['start_timedelta']

            if i + 1 < len(all_timed_lines):
                end_timedelta = all_timed_lines[i + 1]['start_timedelta']
            else:
                base_duration = 2.0
                chars_per_second = 15.0
                estimated_duration = base_duration + (len(line_data['text']) / chars_per_second)
                end_timedelta = start_timedelta + timedelta(seconds=estimated_duration)

            start_time_obj = datetime.min + start_timedelta
            end_time_obj = datetime.min + end_timedelta

            segments_data.append({
                'segment_number': i + 1,
                'start_time': start_time_obj.time().isoformat(timespec='milliseconds'),
                'end_time': end_time_obj.time().isoformat(timespec='milliseconds'),
                'text': line_data['text']
            })
        return segments_data

    def _get_segments_from_data(self, data):
        file = data.get('file')
        raw_text = data.get('raw_text')

        if file:
            if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise ValueError(f"File size cannot exceed {MAX_FILE_SIZE_MB}MB.")
            content = file.read().decode('utf-8')
            filename = file.name.lower()
            if filename.endswith('.srt'):
                return self._parse_srt(content)
            elif filename.endswith('.lrc'):
                return self._parse_lrc(content)
            else:
                raise ValueError("Unsupported file format.")
        elif raw_text:
            if len(raw_text) > MAX_TEXT_INPUT_CHARS:
                raise ValueError(f"Text input cannot exceed {MAX_TEXT_INPUT_CHARS} characters.")
            srt_content = generate_srt_from_text(raw_text)
            return self._parse_srt(srt_content)
        else:
            raise ValueError("Either a file or raw text must be provided.")

    def create_subtitle(self, data, user):
        segments_data = self._get_segments_from_data(data)
        language_code = data.get('language', 'en')
        is_public_status = str(data.get('is_public', 'true')).lower() == 'true'

        subtitle = Subtitle.objects.create(
            song_id=data['song_id'],
            user=user,
            language=language_code,
            is_public=is_public_status,
            title=data.get('title', 'Untitled')
        )
        segments_to_create = [Segment(subtitle=subtitle, **seg_data) for seg_data in segments_data]
        Segment.objects.bulk_create(segments_to_create)
        return subtitle

    def update_subtitle(self, subtitle, user, data):
        if subtitle.user != user:
            raise PermissionError("You can only edit your own subtitles.")

        subtitle.title = data.get('title', subtitle.title)
        subtitle.language = data.get('language', subtitle.language)
        if 'is_public' in data:
            subtitle.is_public = str(data.get('is_public')).lower() == 'true'

        if data.get('file') or data.get('raw_text'):
            segments_data = self._get_segments_from_data(data)
            with transaction.atomic():
                subtitle.segments.all().delete()
                segments_to_create = [Segment(subtitle=subtitle, **seg_data) for seg_data in segments_data]
                Segment.objects.bulk_create(segments_to_create)

        subtitle.save()
        return subtitle

    def delete_subtitle(self, subtitle, user):
        if subtitle.user != user:
            raise PermissionError("You can only delete your own subtitles.")
        subtitle.delete()

    def toggle_like(self, user, subtitle):
        with transaction.atomic():
            like, created = Like.objects.get_or_create(user=user, subtitle=subtitle)
            subtitle_to_update = Subtitle.objects.select_for_update().get(id=subtitle.id)
            if created:
                subtitle_to_update.likes_count += 1
                is_liked = True
            else:
                like.delete()
                subtitle_to_update.likes_count -= 1
                is_liked = False
            subtitle_to_update.save()
        return is_liked, subtitle_to_update.likes_count

    def get_liked_subtitles(self, user):
        return Subtitle.objects.filter(likes__user=user).order_by('-likes__created_at')

    def get_best_public_subtitle(self, song_id, language):
        if not language:
            return None

        return Subtitle.objects.filter(
            song_id=song_id,
            language=language,
            is_public=True
        ).order_by('-likes_count').first()

    def get_available_subtitles_for_song(self, song_id, user, filters=None):
        if filters is None:
            filters = {}
        base_query = Q(song_id=song_id)
        user_access_query = Q(is_public=True) | Q(user=user)

        queryset = Subtitle.objects.filter(base_query & user_access_query).distinct()
        language = filters.get('language')
        if language:
            queryset = queryset.filter(language=language)

        if filters.get('by_user') == 'me':
            queryset = queryset.filter(user=user)

        sort_by = filters.get('sort_by', 'likes_desc')
        if sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-likes_count')

        return queryset

    def set_active_subtitle(self, user, song_id, subtitle):
        if not subtitle.is_public and subtitle.user != user:
            raise PermissionError("User does not have permission to access this subtitle.")
        UserActiveSubtitle.objects.update_or_create(
            user=user, song_id=song_id, defaults={'active_subtitle': subtitle}
        )
        return True

    def unset_active_subtitle(self, user, song_id):
        deleted_count, _ = UserActiveSubtitle.objects.filter(user=user, song_id=song_id).delete()
        return deleted_count > 0

    def get_active_subtitle_for_song(self, user, song_id):
        try:
            active_subtitle_record = UserActiveSubtitle.objects.get(user=user, song_id=song_id)
            return active_subtitle_record.active_subtitle
        except UserActiveSubtitle.DoesNotExist:
            return None