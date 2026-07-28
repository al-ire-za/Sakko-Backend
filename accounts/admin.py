from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import StudentProfile
# Register your models here.

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'اطلاعات پروفایل دانش‌آموزی'

class UserAdmin(BaseUserAdmin):
    inlines = (StudentProfileInline,)




admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(StudentProfile)
