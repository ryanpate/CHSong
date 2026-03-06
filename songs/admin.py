from django.contrib import admin
from .models import Song, Rating, Comment


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'submitted_by', 'submitted_at', 'is_approved')
    list_filter = ('is_approved', 'submitted_at')
    search_fields = ('title', 'artist')
    list_editable = ('is_approved',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('song', 'user', 'stars', 'rated_at')
    list_filter = ('stars',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('song', 'user', 'body_preview', 'parent', 'created_at')
    list_filter = ('created_at',)

    def body_preview(self, obj):
        return obj.body[:50]
    body_preview.short_description = 'Comment'
