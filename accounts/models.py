from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    FIELD_CHOICES = [
       ('تجربی', 'تجربی'),
        ('ریاضی', 'ریاضی'),
        ('انسانی', 'انسانی')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="User")
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Age")
    field = models.CharField(max_length=20, choices=FIELD_CHOICES, default='Experimental', verbose_name="Study Field")
    parent_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Parent Phone")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.field})"


class Friendship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships', verbose_name="USER")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_of', verbose_name="Friend")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # جلوگیری از اضافه کردن تکراری یک دوست
        unique_together = ('user', 'friend')
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friends'

    def __str__(self):
        return f"{self.user.username} -> {self.friend.username}"