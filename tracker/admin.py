from django.contrib import admin
from .models import Task, StudySession, DailySleepLog, UserTaskGroup, UserStudyGroup, UserSleepGroup

class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ('date', 'text', 'completed')
    ordering = ('-date',)

# ۲. ادمین اختصاصی برای لیست تسک‌های هر کاربر (بدون فیلدهای اضافه کاربر)
@admin.register(UserTaskGroup)
class UserTaskGroupAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'get_task_count')
    search_fields = ('username', 'first_name', 'last_name')
    inlines = [TaskInline]

    # 🌟 تمام فیلدهای اضافی User (ایمیل، پسورد، لست نیم و...) مخفی می‌شوند
    # و فقط نام کاربری (آن هم فقط‌خواندنی) بالای صفحه می‌ماند
    readonly_fields = ('username',)
    fieldsets = (
        (None, {
            'fields': ('username',)
        }),
    )

    # نمایش تعداد کل تسک‌ها در جدول اصلی
    def get_task_count(self, obj):
        return obj.tasks.count()
    get_task_count.short_description = "SUM TASK"

    # غیرفعال کردن امکان ساخت کاربر جدید از این بخش
    def has_add_permission(self, request):
        return False

class StudySessionInline(admin.TabularInline):
    model = StudySession
    extra = 0
    fields = ('date', 'subject', 'topic', 'start_time', 'end_time', 'test_count')
    ordering = ('-date',)


# ۲. ادمین اختصاصی برای پارت‌های مطالعه کاربر
@admin.register(UserStudyGroup)
class UserStudyGroupAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'get_total_sessions', 'get_total_tests')
    search_fields = ('username', 'first_name', 'last_name')
    inlines = [StudySessionInline]

    # مخفی کردن فیلدهای اضافی کاربر
    readonly_fields = ('username',)
    fieldsets = (
        (None, {
            'fields': ('username',)
        }),
    )

    # محاسبه تعداد پارت‌های ثبت شده
    def get_total_sessions(self, obj):
        return obj.study_sessions.count()
    get_total_sessions.short_description = "Number of sections"

    # محاسبه تعداد کل تست‌های زده شده توسط کاربر
    def get_total_tests(self, obj):
        return sum(session.test_count for session in obj.study_sessions.all())
    get_total_tests.short_description = "SUM TEST"

    def has_add_permission(self, request):
        return False


class DailySleepLogInline(admin.TabularInline):
    model = DailySleepLog
    extra = 0
    fields = ('date', 'sleep_time', 'wake_time')
    readonly_fields = ('date',)  # 👈 برای جلوگیری از ارور auto_now_add
    ordering = ('-date',)

# ۲. ادمین اختصاصی برای گزارش خواب کاربر
@admin.register(UserSleepGroup)
class UserSleepGroupAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'get_total_sleep_logs')
    search_fields = ('username', 'first_name', 'last_name')
    inlines = [DailySleepLogInline]

    # مخفی کردن فیلدهای اضافی کاربر
    readonly_fields = ('username',)
    fieldsets = (
        (None, {
            'fields': ('username',)
        }),
    )

    # نمایش تعداد روزهای ثبت شده خواب
    def get_total_sleep_logs(self, obj):
        return obj.sleep_logs.count()
    get_total_sleep_logs.short_description = "تعداد روزهای ثبت شده"

    def has_add_permission(self, request):
        return False
