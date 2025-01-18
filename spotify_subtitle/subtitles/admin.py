from django.contrib import admin
from .models import Subtitle, Segment
from django.utils.html import format_html


@admin.register(Subtitle)
class SubtitleAdmin(admin.ModelAdmin):
    list_display = ('song_id', 'user', 'created_at')
    search_fields = ('song_id', 'user__username')


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ('subtitle', 'segment_number', 'formatted_start_time', 'formatted_end_time', 'short_text')

    def formatted_start_time(self, obj):
        return self.format_time(obj.start_time)
    formatted_start_time.short_description = 'Start Time'

    def formatted_end_time(self, obj):
        return self.format_time(obj.end_time)
    formatted_end_time.short_description = 'End Time'

    @staticmethod
    def format_time(time_obj):
        return time_obj.strftime("%H:%M:%S.%f")[:-3]

    def short_text(self, obj):
        return obj.text[:15] + '...' if len(obj.text) > 50 else obj.text

    short_text.short_description = 'Text'
