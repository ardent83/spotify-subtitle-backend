from django.contrib import admin
from .models import Subtitle


@admin.register(Subtitle)
class SubtitleAdmin(admin.ModelAdmin):
    list_display = ('song_id', 'subtitle_text', 'user', 'created_at')
    search_fields = ('song_id', 'user__username')
