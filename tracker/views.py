from rest_framework import viewsets, permissions, status
from .models import Task, StudySession, DailySleepLog
from .serializers import TaskSerializer, StudySessionSerializer, DailySleepLogSerializer
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(date=date_param)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudySessionViewSet(viewsets.ModelViewSet):
    serializer_class = StudySessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = StudySession.objects.filter(user=self.request.user)
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(date=date_param)
        else:
            queryset = queryset.filter(date=timezone.localdate())
        return queryset.order_by('start_time')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SleepLogViewSet(viewsets.ModelViewSet):
    serializer_class = DailySleepLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = DailySleepLog.objects.filter(user=self.request.user)
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(date=date_param)
        else:
            queryset = queryset.filter(date=timezone.localdate())
        return queryset

    def create(self, request, *args, **kwargs):
        sleep_time = request.data.get('sleep_time')
        wake_time = request.data.get('wake_time')
        target_date = request.data.get('date') or timezone.localdate()

        if not sleep_time or not wake_time:
            return Response({'error': 'زمان خواب و بیداری الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)

        sleep_log, created = DailySleepLog.objects.update_or_create(
            user=request.user,
            date=target_date,
            defaults={
                'sleep_time': sleep_time,
                'wake_time': wake_time
            }
        )

        serializer = self.get_serializer(sleep_log)
        return Response(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)


class LeaderboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', 'day')  # day, week, month
        today = timezone.localdate()

        # تعیین بازه زمانی
        if period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        else:  # day
            start_date = today

        sessions = StudySession.objects.filter(date__gte=start_date).select_related('user')
        user_stats = {}

        for session in sessions:
            u = session.user
            if u.id not in user_stats:
                user_stats[u.id] = {
                    "id": u.id,
                    "username": u.username,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                    "full_name": f"{u.first_name} {u.last_name}".strip() or u.username,
                    "total_seconds": 0,
                    "total_tests": 0,
                }

            t1 = timedelta(hours=session.start_time.hour, minutes=session.start_time.minute, seconds=session.start_time.second)
            t2 = timedelta(hours=session.end_time.hour, minutes=session.end_time.minute, seconds=session.end_time.second)
            duration = (t2 - t1).total_seconds()
            if duration < 0:
                duration += 24 * 3600  # پشتیبانی از پارت‌های مطالعه عبور کرده از نیمه‌شب
            
            if duration > 0:
                user_stats[u.id]["total_seconds"] += duration
            
            user_stats[u.id]["total_tests"] += session.test_count

        leaderboard_data = []
        for item in user_stats.values():
            if item["total_seconds"] > 0 or item["total_tests"] > 0:
                item["total_hours"] = round(item["total_seconds"] / 3600, 1)
                leaderboard_data.append(item)

        sorted_leaderboard = sorted(
            leaderboard_data,
            key=lambda x: (x['total_seconds'], x['total_tests']),
            reverse=True
        )[:10]

        return Response(sorted_leaderboard)