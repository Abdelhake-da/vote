from django.contrib import admin
from .models import Photo, Vote

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'votes')
    search_fields = ('title',)

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('photo', 'session_key', 'timestamp')
    list_filter = ('timestamp',)
