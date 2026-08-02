from rest_framework import viewsets, permissions, status
from .models import Task, StudySession, DailySleepLog
from .serializers import TaskSerializer, StudySessionSerializer, DailySleepLogSerializer
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta
from django.db.models import Sum, F, ExpressionWrapper, DurationField
from django.contrib.auth.models import User

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # فقط کارهای کاربر لاگین شده را برمی‌گرداند
        queryset = Task.objects.filter(user=self.request.user)
        # اگر تاریخ در پارامترهای URL بود، بر اساس آن فیلتر کن
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(date=date_param)
        return queryset

    def perform_create(self, serializer):
        # موقع ثبت task جدید، کاربر فعلی به عنوان owner ذخیره می‌شود
        serializer.save(user=self.request.user)

class StudySessionViewSet(viewsets.ModelViewSet):
    serializer_class = StudySessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StudySession.objects.filter(user=self.request.user, date=timezone.now().date())

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SleepLogViewSet(viewsets.ModelViewSet):
    serializer_class = DailySleepLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DailySleepLog.objects.filter(user=self.request.user, date=timezone.now().date())

    def create(self, request, *args, **kwargs):
        sleep_time = request.data.get('sleep_time')
        wake_time = request.data.get('wake_time')

        if not sleep_time or not wake_time:
            return Response({'error': 'زمان خواب و بیداری الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)

        sleep_log, created = DailySleepLog.objects.update_or_create(
            user=request.user,
            date=timezone.now().date(),
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
        today = timezone.now().date()

        # تعیین بازه زمانی
        if period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        else:  # day
            start_date = today

        # محاسبه مجموع زمان مطالعه و تست برای هر کاربر
        # محاسبه اختلاف start_time و end_time به ثانیه
        sessions = StudySession.objects.filter(date__gte=start_date)

        users = User.objects.all()
        leaderboard_data = []

        for user in users:
            user_sessions = sessions.filter(user=user)
            
            total_seconds = 0
            total_tests = 0

            for session in user_sessions:
                # محاسبه مدت زمان جلسه مطالعه
                t1 = timedelta(hours=session.start_time.hour, minutes=session.start_time.minute, seconds=session.start_time.second)
                t2 = timedelta(hours=session.end_time.hour, minutes=session.end_time.minute, seconds=session.end_time.second)
                
                duration = (t2 - t1).total_seconds()
                if duration > 0:
                    total_seconds += duration
                
                total_tests += session.test_count

            # اضافه کردن به لیست اگر حداقل یک بار مطالعه داشته است
            if total_seconds > 0 or total_tests > 0:
                hours = round(total_seconds / 3600, 1)  # تبدیل ثانیه به ساعت با یک رقم اعشار
                leaderboard_data.append({
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "full_name": f"{user.first_name} {user.last_name}".strip() or user.username,
                    "total_hours": hours,
                    "total_seconds": total_seconds,
                    "total_tests": total_tests,
                })

        # مرتب‌سازی: اول بر اساس بیشترین زمان مطالعه (total_seconds)، در صورت برابر بودن بر اساس تعداد تست (total_tests)
        sorted_leaderboard = sorted(
            leaderboard_data,
            key=lambda x: (x['total_seconds'], x['total_tests']),
            reverse=True
        )[:10]  # فقط ۱۰ نفر برتر

        return Response(sorted_leaderboard)