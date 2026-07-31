from rest_framework import serializers
from .models import Task, StudySession, DailySleepLog

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'text', 'completed', 'date']


class StudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySession
        fields = ['id', 'subject', 'topic', 'start_time', 'end_time', 'test_count', 'date']

class DailySleepLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySleepLog
        fields = ['id', 'sleep_time', 'wake_time', 'date']