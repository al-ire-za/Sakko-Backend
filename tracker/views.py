from rest_framework import viewsets, permissions, status
from .models import Task, StudySession, DailySleepLog
from .serializers import TaskSerializer, StudySessionSerializer, DailySleepLogSerializer
from django.utils import timezone
from rest_framework.response import Response

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