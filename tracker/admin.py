from django.contrib import admin
from .models import Task, StudySession, DailySleepLog

admin.site.register(Task)
admin.site.register(StudySession)
admin.site.register(DailySleepLog)
