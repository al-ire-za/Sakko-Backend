from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

# ۱. پروفایل دانش‌آموز
class StudentProfile(models.Model):
    FIELD_CHOICES = [
        ('تجربی', 'تجربی'),
        ('ریاضی', 'ریاضی'),
        ('انسانی', 'انسانی'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', verbose_name="User")
    avatar = models.ImageField(upload_to='avatars/students/', null=True, blank=True, verbose_name='img')
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Age")
    field = models.CharField(max_length=20, choices=FIELD_CHOICES, default='تجربی', verbose_name="Study Field")
    parent_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Parent Phone")
    
    # 🌟 مشاورِ انتخابی دانش‌آموز (می‌تواند خالی باشد تا زمانی که مشاور انتخاب کند)
    consultant = models.ForeignKey(
        'ConsultantProfile', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='students',
        verbose_name="Selected Consultant"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

    def __str__(self):
        return f"دانش‌آموز: {self.user.username} ({self.field})"


# ۲. 🌟 پروفایل مشاور (جدید)
class ConsultantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='consultant_profile', verbose_name="User")
    bio = models.TextField(blank=True, verbose_name="rezomeh")
    avatar = models.ImageField(upload_to='consultants/', null=True, blank=True, verbose_name="img")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Phone Number")
    max_capacity = models.PositiveIntegerField(default=10, verbose_name="Max Student Capacity")
    created_at = models.DateTimeField(auto_now_add=True)

    # 🌟 متد محاسبه میانگین امتیاز مشاور
    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.score for r in ratings) / ratings.count(), 1)
        return 0.0

    @property
    def active_students_count(self):
        return self.students.count()

    # تعداد کل امتیازدهندگان
    @property
    def total_ratings_count(self):
        return self.ratings.count()

    @property
    def is_full(self):
        return self.active_students_count >= self.max_capacity

    class Meta:
        verbose_name = "Consultant Profile"
        verbose_name_plural = "Consultant Profiles"

    def __str__(self):
        return f"مشاور: {self.user.get_full_name() or self.user.username}"


# ۳. 🌟 مدل امتیازدهی دانش‌آموز به مشاور (جدید)
class ConsultantRating(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    consultant = models.ForeignKey(ConsultantProfile, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Score(1 to 5)"
    )
    comment = models.TextField(blank=True, null=True, verbose_name="Student's opinion")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # جلوگیری از ثبت بیش از یک امتیاز توسط یک دانش‌آموز برای یک مشاور
        unique_together = ('student', 'consultant')
        verbose_name = "Consultant Rating"
        verbose_name_plural = "Consultant Ratings"

    def __str__(self):
        return f"امتیاز {self.score} از {self.student.username} به {self.consultant.user.username}"


# ۴. مدل دوستی (قبلی خودت)
class Friendship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships', verbose_name="USER")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_of', verbose_name="Friend")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friends'

    def __str__(self):
        return f"{self.user.username} -> {self.friend.username}"


class StudentTaskFile(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_files')
    consultant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_files')
    file = models.FileField(upload_to='student_tasks/')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} -> {self.consultant.username}"


class ConsultantProgram(models.Model):
    consultant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_programs",
        verbose_name="مشاور"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_programs",
        verbose_name="دانش‌آموز"
    )
    title = models.CharField(max_length=255, verbose_name="عنوان برنامه")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    file = models.FileField(upload_to="consultant_programs/", verbose_name="فایل برنامه")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.student.username}"