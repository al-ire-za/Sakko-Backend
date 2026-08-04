from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Course
from .serializers import CourseSerializer

class CourseListAPIView(ListCreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # ۱. تشخیص دقیق نقش کاربر بر اساس مدل‌های سیستم شما
        if hasattr(user, 'consultant_profile'):
            user_role = 'consultant'
        else:
            user_role = 'student'

        # ۲. فیلتر کردن دوره‌ها (دوره‌های مخصوص نقش + دوره‌های عمومی)
        return Course.objects.filter(
            Q(target_audience=user_role) | Q(target_audience=Course.TargetAudience.PUBLIC)
        )