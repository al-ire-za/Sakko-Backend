from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import StudentProfile, ConsultantProfile, ConsultantRating, Friendship, StudentTaskFile, ConsultantProgram



# ==========================================
# ۱. فرم‌های سفارشی جهت ویرایش نام و نام خانوادگی
# ==========================================

class StudentProfileAdminForm(forms.ModelForm):
    first_name = forms.CharField(label="name", required=False)
    last_name = forms.CharField(label="last name", required=False)

    class Meta:
        model = StudentProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and hasattr(self.instance, 'user') and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        if profile.user:
            profile.user.first_name = self.cleaned_data.get('first_name', '')
            profile.user.last_name = self.cleaned_data.get('last_name', '')
            profile.user.save()
        if commit:
            profile.save()
        return profile


class ConsultantProfileAdminForm(forms.ModelForm):
    first_name = forms.CharField(label="name", required=False)
    last_name = forms.CharField(label="last name", required=False)

    class Meta:
        model = ConsultantProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and hasattr(self.instance, 'user') and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        if profile.user:
            profile.user.first_name = self.cleaned_data.get('first_name', '')
            profile.user.last_name = self.cleaned_data.get('last_name', '')
            profile.user.save()
        if commit:
            profile.save()
        return profile


# ==========================================
# ۲. اینلاین‌ها برای بخش مدیریت کاربران (User)
# ==========================================

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    extra = 0
    verbose_name_plural = 'اطلاعات پروفایل دانش‌آموزی'


class ConsultantProfileInline(admin.StackedInline):
    model = ConsultantProfile
    can_delete = False
    extra = 0
    verbose_name_plural = 'اطلاعات پروفایل مشاوری'


class FriendshipInline(admin.TabularInline):
    model = Friendship
    fk_name = "user"
    extra = 0
    autocomplete_fields = ['friend']
    verbose_name = 'دوست'
    verbose_name_plural = 'لیست دوستان'


# ==========================================
# ۳. سفارشی‌سازی مدیریت کاربران (UserAdmin)
# ==========================================

class CustomUserAdmin(BaseUserAdmin):
    # تنظیم کادرهای فرم ویرایش کاربر جهت نمایش اطلاعات شخصی در بالا
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email')}),
        ('مجوزها و دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'first_name', 'last_name', 'email', 'get_role', 'get_friends_count')

    # مدیریت شرطی اینلاین‌ها بر اساس نقش کاربر
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        inline_instances = []

        if hasattr(obj, 'student_profile'):
            inline_instances.append(StudentProfileInline(self.model, self.admin_site))
        elif hasattr(obj, 'consultant_profile'):
            inline_instances.append(ConsultantProfileInline(self.model, self.admin_site))

        inline_instances.append(FriendshipInline(self.model, self.admin_site))

        return inline_instances

    def get_role(self, obj):
        if hasattr(obj, 'consultant_profile'):
            return "consultant"
        elif hasattr(obj, 'student_profile'):
            return "student"
        return "کاربر عادی"
    
    get_role.short_description = 'ROLE'

    def get_friends_count(self, obj):
        return Friendship.objects.filter(user=obj).count()
    
    get_friends_count.short_description = 'NUMBER OF FRIEND'


# ==========================================
# ۴. ثبت مدل‌ها در ادمین
# ==========================================

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    form = StudentProfileAdminForm
    list_display = ('user', 'get_first_name', 'get_last_name', 'field', 'age', 'consultant', 'created_at')
    list_filter = ('field',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    # 🌟 مرتب‌سازی هوشمند فیلدها بدون ارور Unknown Field
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        # حذف first_name و last_name در صورت وجود تکراری
        fields = [f for f in fields if f not in ('first_name', 'last_name')]
        
        # درج نام و نام خانوادگی بلافاصله بعد از فیلد user
        if 'user' in fields:
            user_index = fields.index('user')
            fields.insert(user_index + 1, 'first_name')
            fields.insert(user_index + 2, 'last_name')
        else:
            fields = ['first_name', 'last_name'] + fields
        return fields

    def get_first_name(self, obj):
        return obj.user.first_name if obj.user else ''
    get_first_name.short_description = 'name'

    def get_last_name(self, obj):
        return obj.user.last_name if obj.user else ''
    get_last_name.short_description = 'last name'


@admin.register(ConsultantProfile)
class ConsultantProfileAdmin(admin.ModelAdmin):
    form = ConsultantProfileAdminForm
    list_display = ('user', 'get_first_name', 'get_last_name', 'average_rating', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('created_at',)

    # 🌟 مرتب‌سازی هوشمند فیلدها بدون ارور Unknown Field
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        # حذف first_name و last_name در صورت وجود تکراری
        fields = [f for f in fields if f not in ('first_name', 'last_name')]
        
        # درج نام و نام خانوادگی بلافاصله بعد از فیلد user
        if 'user' in fields:
            user_index = fields.index('user')
            fields.insert(user_index + 1, 'first_name')
            fields.insert(user_index + 2, 'last_name')
        else:
            fields = ['first_name', 'last_name'] + fields
        return fields

    def get_first_name(self, obj):
        return obj.user.first_name if obj.user else ''
    get_first_name.short_description = 'name'

    def get_last_name(self, obj):
        return obj.user.last_name if obj.user else ''
    get_last_name.short_description = 'last name'


@admin.register(ConsultantRating)
class ConsultantRatingAdmin(admin.ModelAdmin):
    list_display = ('student', 'consultant', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('student__username', 'consultant__user__username')


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'created_at') if hasattr(Friendship, 'created_at') else ('user', 'friend')
    search_fields = ('user__username', 'friend__username')


@admin.register(StudentTaskFile)
class StudentTaskFileAdmin(admin.ModelAdmin):
    list_display = ('student', 'consultant', 'file', 'created_at')
    search_fields = ('student__username', 'consultant__username', 'description')
    list_filter = ('created_at',)


@admin.register(ConsultantProgram)
class ConsultantProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'consultant', 'student', 'created_at')
    search_fields = ('title', 'consultant__username', 'student__username')
    list_filter = ('created_at',)


# آن‌رجیستر کردن User قبلی و ثبت CustomUserAdmin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)