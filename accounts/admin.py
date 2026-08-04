from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import StudentProfile, ConsultantProfile, ConsultantRating, Friendship


# ۱. اینلاین پروفایل دانش‌آموز
class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'اطلاعات پروفایل دانش‌آموزی'


# ۲. 🌟 اینلاین پروفایل مشاور (جدید)
class ConsultantProfileInline(admin.StackedInline):
    model = ConsultantProfile
    can_delete = False
    verbose_name_plural = 'اطلاعات پروفایل مشاوری'


# ۳. اینلاین لیست دوستان کاربر
class FriendshipInline(admin.TabularInline):
    model = Friendship
    fk_name = "user"
    extra = 0
    autocomplete_fields = ['friend']
    verbose_name = 'دوست'
    verbose_name_plural = 'لیست دوستان'


# ۴. سفارشی‌سازی مدیریت کاربران در ادمین
class CustomUserAdmin(BaseUserAdmin):
    # شامل هر سه اینلاین: دانش‌آموز، مشاور، و دوستان
    inlines = (StudentProfileInline, ConsultantProfileInline, FriendshipInline)
    
    # ستون‌های صفحه اصلی کاربران
    list_display = BaseUserAdmin.list_display + ('get_role', 'get_friends_count')

    # متد برای نمایش نقش کاربر در جدول
    def get_role(self, obj):
        if hasattr(obj, 'consultant_profile'):
            return "consultant"
        elif hasattr(obj, 'student_profile'):
            return "student"
        return "کاربر عادی"
    
    get_role.short_description = 'ROLE'

    # شمارش تعداد دوستان
    def get_friends_count(self, obj):
        return Friendship.objects.filter(user=obj).count()
    
    get_friends_count.short_description = 'NUMBER OF FRIEND'


# ۵. 🌟 ثبت مدل مشاور در ادمین
@admin.register(ConsultantProfile)
class ConsultantProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'average_rating', 'total_ratings_count', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    list_filter = ('created_at',)


# ۶. 🌟 ثبت مدل امتیازدهی مشاوران در ادمین
@admin.register(ConsultantRating)
class ConsultantRatingAdmin(admin.ModelAdmin):
    list_display = ('student', 'consultant', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('student__username', 'consultant__user__username')


# ۷. ثبت مدل دوستی
@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'created_at') if hasattr(Friendship, 'created_at') else ('user', 'friend')
    search_fields = ('user__username', 'friend__username')


# ۸. ثبت مدل پروفایل دانش‌آموز
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'field', 'age', 'consultant', 'created_at')
    list_filter = ('field',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    


# آن‌رجیستر کردن User قبلی و ثبت CustomUserAdmin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)