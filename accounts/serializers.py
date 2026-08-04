from rest_framework import serializers
from django.contrib.auth.models import User
from .models import StudentProfile, ConsultantProfile, ConsultantRating, Friendship
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

try:
    from tracker.models import StudySession
except ImportError:
    StudySession = None


# ۱. سریالایزر ثبت‌نام هوشمند (دانش‌آموز یا مشاور)
class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=['student', 'consultant'], default='student', write_only=True)
    
    # فیلدهای مخصوص دانش‌آموز
    age = serializers.IntegerField(required=False, allow_null=True)
    field = serializers.CharField(max_length=20, default='تجربی', required=False)
    parent_phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    
    # فیلدهای مخصوص مشاور
    bio = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name', 
            'role', 'age', 'field', 'parent_phone', 'bio', 'phone'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        role = validated_data.pop('role', 'student')
        
        # جدا کردن فیلدهای دانش‌آموز
        age = validated_data.pop('age', None)
        field = validated_data.pop('field', 'تجربی')
        parent_phone = validated_data.pop('parent_phone', '')
        
        # جدا کردن فیلدهای مشاور
        bio = validated_data.pop('bio', '')
        phone = validated_data.pop('phone', '')

        # ساخت کاربر
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        # ایجاد پروفایل مربوطه بر اساس نقش
        if role == 'consultant':
            ConsultantProfile.objects.create(
                user=user,
                bio=bio,
                phone=phone
            )
        else:
            StudentProfile.objects.create(
                user=user,
                age=age,
                field=field,
                parent_phone=parent_phone
            )

        return user


# ۲. سریالایزر پروفایل کاربر متصل (دریافت اطلاعات خود کاربر)
class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    field = serializers.SerializerMethodField()
    parent_phone = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'avatar', 'age', 'field', 'parent_phone', 'bio', 'phone', 'average_rating'
        ]

    def get_role(self, obj):
        if hasattr(obj, 'consultant_profile'):
            return 'consultant'
        return 'student'

    def get_age(self, obj):
        if hasattr(obj, 'student_profile'):
            return obj.student_profile.age
        return None

    def get_field(self, obj):
        if hasattr(obj, 'student_profile'):
            return obj.student_profile.field
        return None

    def get_parent_phone(self, obj):
        if hasattr(obj, 'student_profile'):
            return obj.student_profile.parent_phone
        return None

    def get_bio(self, obj):
        if hasattr(obj, 'consultant_profile'):
            return obj.consultant_profile.bio
        return None

    def get_phone(self, obj):
        if hasattr(obj, 'consultant_profile'):
            return obj.consultant_profile.phone
        return None

    def get_average_rating(self, obj):
        if hasattr(obj, 'consultant_profile'):
            return obj.consultant_profile.average_rating
        return None
    
    def get_avatar(self, obj):
        request = self.context.get('request')
        avatar_file = None
        
        if hasattr(obj, 'student_profile') and obj.student_profile.avatar:
            avatar_file = obj.student_profile.avatar
        elif hasattr(obj, 'consultant_profile') and obj.consultant_profile.avatar:
            avatar_file = obj.consultant_profile.avatar

        if avatar_file and request:
            return request.build_absolute_uri(avatar_file.url)
        return None


# ۳. سریالایزر لیست مشاوران (برای نمایش به دانش‌آموزان)
class ConsultantListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    bio = serializers.CharField(source='consultant_profile.bio', read_only=True)
    phone = serializers.CharField(source='consultant_profile.phone', read_only=True)
    average_rating = serializers.FloatField(source='consultant_profile.average_rating', read_only=True)
    total_ratings_count = serializers.IntegerField(source='consultant_profile.total_ratings_count', read_only=True)
    consultant_profile_id = serializers.IntegerField(source='consultant_profile.id', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'consultant_profile_id', 'username', 'full_name', 
            'bio', 'phone', 'average_rating', 'total_ratings_count'
        ]

    def get_full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else obj.username


# ۴. سریالایزر ثبت امتیاز توسط دانش‌آموز
class ConsultantRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultantRating
        fields = ['id', 'consultant', 'score', 'comment', 'created_at']
        read_only_fields = ['student']

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


# ۵. سریالایزر دوستان (قبلی خودت)
class FriendUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    last_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'last_status']

    def get_full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else obj.username

    def get_last_status(self, obj):
        if StudySession:
            latest = StudySession.objects.filter(user=obj).order_by('-date', '-id').first()
            if latest:
                return f"در حال مطالعه {latest.subject}"
        return "آنلاین"


# ۶. سریالایزر افزودن دوست (قبلی خودت)
class AddFriendSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)

    def validate_username(self, value):
        request_user = self.context['request'].user
        
        if value == request_user.username:
            raise serializers.ValidationError("نمی‌توانید نام کاربری خودتان را وارد کنید.")
            
        try:
            target_user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("کاربری با این نام کاربری یافت نشد.")
            
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # مشخص کردن نقش کاربر
        user = self.user
        role = 'consultant' if hasattr(user, 'consultant_profile') else 'student'
        
        # اضافه کردن اطلاعات کاربر به پاسخ لاگین
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': role,
            'is_consultant': role == 'consultant'
        }
        return data