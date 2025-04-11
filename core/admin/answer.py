from django.contrib import admin
from core.models import Answer


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'author', 'created_at', 'total_likes')
    search_fields = ('content',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'likes') 