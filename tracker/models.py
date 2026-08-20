from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ۱. مدل کارهای دفترچه برنامه‌ریزی
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', verbose_name="User")
    text = models.CharField(max_length=255, verbose_name="Task Title")
    completed = models.BooleanField(default=False, verbose_name="Completed Status")
    date = models.DateField(verbose_name="Task Date")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return f"{self.user.username} - {self.text[:20]}"


# ۲. مدل ثبت بازه مطالعه روزانه
class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions', verbose_name="User")
    subject = models.CharField(max_length=100, verbose_name="Subject")
    topic = models.CharField(max_length=150, blank=True, verbose_name="Topic")
    start_time = models.TimeField(verbose_name="Start Time")
    end_time = models.TimeField(verbose_name="End Time")
    test_count = models.PositiveIntegerField(default=0, verbose_name="Test Count")
    date = models.DateField(default=timezone.localdate, verbose_name="Date")

    class Meta:
        verbose_name = "Study Session"
        verbose_name_plural = "Study Sessions"

    def __str__(self):
        return f"{self.user.username} - {self.subject} ({self.test_count} tests)"


# ۳. مدل الگوی خواب روزانه
class DailySleepLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleep_logs', verbose_name="User")
    sleep_time = models.TimeField(verbose_name="Sleep Time")
    wake_time = models.TimeField(verbose_name="Wake Time")
    date = models.DateField(default=timezone.localdate, verbose_name="Date")


    class Meta:
        unique_together = ('user', 'date')
        verbose_name = "Daily Sleep Log"
        verbose_name_plural = "Daily Sleep Logs"

    def __str__(self):
        return f"{self.user.username} Sleep Log ({self.date})"

# مدل ساختگی فقط برای تغییر ظاهر ادمین
class UserTaskGroup(User):
    class Meta:
        proxy = True
        verbose_name = "Task"
        verbose_name_plural = "Tasks"


# مدل ساختگی برای گروه‌بندی پارت‌های مطالعه بر اساس کاربر
class UserStudyGroup(User):
    class Meta:
        proxy = True
        verbose_name = "Study Session"
        verbose_name_plural = "Study Sessions"


# مدل ساختگی برای گروه‌بندی خواب کاربران
class UserSleepGroup(User):
    class Meta:
        proxy = True
        verbose_name = "Daily Sleep Log"
        verbose_name_plural = "Daily Sleep Log"