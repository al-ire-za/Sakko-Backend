from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    # ۱. تعریف انواع مخاطبین دوره
    class TargetAudience(models.TextChoices):
        STUDENT = 'student', 'دانش‌آموز'
        CONSULTANT = 'consultant', 'مشاور'
        PUBLIC = 'public', 'عمومی'

    title = models.CharField(max_length=200, verbose_name="Course Title")
    description = models.TextField(blank=True, verbose_name="Description")
    instructor = models.CharField(max_length=100, blank=True, verbose_name="Instructor")
    
    # ۲. اضافه کردن فیلد مخاطب دوره
    target_audience = models.CharField(
        max_length=20,
        choices=TargetAudience.choices,
        default=TargetAudience.PUBLIC,
        verbose_name="Target Audience"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    icon_name = models.CharField(max_length=50, default='BookOpen', verbose_name="Icon Name")
    dark_color = models.CharField(max_length=50, default='text-indigo-400', verbose_name="Dark Mode Color Class")
    light_color = models.CharField(max_length=50, default='text-indigo-600', verbose_name="Light Mode Color Class")

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return f"{self.title} ({self.get_target_audience_display()})"


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', verbose_name="User")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name="Course")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

    def __str__(self):
        return f"{self.user.username} -> {self.course.title}"