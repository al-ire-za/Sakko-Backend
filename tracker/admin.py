from django.contrib import admin
from .models import Task, StudySession, DailySleepLog

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'date', 'completed', 'created_at')
    list_filter = ('completed', 'date', 'user')
    search_fields = ('text', 'user__username')


admin.site.register(StudySession)
admin.site.register(DailySleepLog)
