from django.shortcuts import render, get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User

# ایمپورت مدل‌ها و سریالایزرهای لازم
from .models import Friendship
from .serializers import (
    RegisterSerializer, 
    UserProfileSerializer, 
    FriendUserSerializer, 
    AddFriendSerializer
)


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class UserProfileView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class FriendListAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # ۱. دریافت لیست دوستان کاربر جاری
    def get(self, request):
        # دریافت شناسه تمام کاربرانی که دوست کاربر فعلی هستند
        friend_ids = Friendship.objects.filter(user=request.user).values_list('friend_id', flat=True)
        friends = User.objects.filter(id__in=friend_ids)
        
        serializer = FriendUserSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ۲. افزودن دوست جدید با username
    def post(self, request):
        serializer = AddFriendSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            target_username = serializer.validated_data['username']
            target_user = get_object_or_404(User, username=target_username)
            
            # بررسی اینکه قبلاً اضافه نشده باشد
            if Friendship.objects.filter(user=request.user, friend=target_user).exists():
                return Response(
                    {"username": ["این کاربر قبلاً در لیست دوستان شما قرار دارد."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # ایجاد رابطه دوستی (دو طرفه)
            Friendship.objects.create(user=request.user, friend=target_user)
            Friendship.objects.create(user=target_user, friend=request.user)
            
            return Response(
                {
                    "message": "کاربر با موفقیت اضافه شد.",
                    "friend": FriendUserSerializer(target_user).data
                },
                status=status.HTTP_201_CREATED
            )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)