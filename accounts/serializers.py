from rest_framework import serializers
from django.contrib.auth.models import User
from .models import StudentProfile

class RegisterSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(required=False, allow_null=True)
    field = serializers.CharField(max_length=20, default='تجربی')
    parent_phone = serializers.CharField(max_length=15, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'age', 'field', 'parent_phone']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # جدا کردن فیلدهای مربوط به profile
        age = validated_data.pop('age', None)
        field = validated_data.pop('field', 'تجربی')
        parent_phone = validated_data.pop('parent_phone', '')

        # ساخت کاربر جدید
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        # ساخت پروفایل دانش‌آموز متصل به کاربر
        StudentProfile.objects.create(
            user=user,
            age=age,
            field=field,
            parent_phone=parent_phone
        )

        return user

class UserProfileSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(source='profile.age', read_only=True)
    field = serializers.CharField(source='profile.field', read_only=True)
    parent_phone = serializers.CharField(source='profile.parent_phone', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'age', 'field', 'parent_phone']