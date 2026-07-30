from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import StudentProfile
from .models import Friendship

# Register your models here.


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'اطلاعات پروفایل دانش‌آموزی'

class UserAdmin(BaseUserAdmin):
    inlines = (StudentProfileInline,)


class FriendshipInline(admin.TabularInline):
    model = Friendship
    # اگر در مدل دو کلید خارجی به کاربر دارید (مثلا user و friend)، یکی را مشخص کنید:
    fk_name = "user" 
    extra = 0 # جلوگیری از ایجاد سطرهای خالی اضافه
    autocomplete_fields = ['friend'] # برای جستجوی سریع‌تر دوست
    verbose_name = 'Friend'
    verbose_name_plural = 'Friends'

    

class CustomUserAdmin(BaseUserAdmin):
    # ترکیب هر دو اینلاین در صفحه کاربر
    inlines = (StudentProfileInline, FriendshipInline)
    
    # اضافه کردن ستون تعداد دوستان به جدول اصلی کاربران
    list_display = BaseUserAdmin.list_display + ('get_friends_count',)

    def get_friends_count(self, obj):
        # شمارش تعداد دوستی‌های ثبت‌شده این کاربر
        return Friendship.objects.filter(user=obj).count()
    
    get_friends_count.short_description = 'COUNT FRIENDS'

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'created_at') if hasattr(Friendship, 'created_at') else ('user', 'friend')
    search_fields = ('user__username', 'friend__username')

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
admin.site.register(StudentProfile)
