from django.shortcuts import render, get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, ConsultantListSerializer, StudentTaskFileSerializer, UserProfileSerializer
from .models import StudentTaskFile
from rest_framework.parsers import MultiPartParser, FormParser

# ایمپورت مدل‌ها و سریالایزرهای لازم
from .models import Friendship, ConsultantProfile, ConsultantRating, StudentProfile
from .serializers import (
    RegisterSerializer, 
    UserProfileSerializer, 
    FriendUserSerializer, 
    AddFriendSerializer,
    ConsultantListSerializer,
    ConsultantRatingSerializer
)


# ۱. ثبت‌نام (دانش‌آموز یا مشاور)
class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


# ۲. پروفایل کاربر جاری
class UserProfileView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


# ۳. مدیریت دوستان (قبلی خودت)
class FriendListAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # دریافت لیست دوستان
    def get(self, request):
        friend_ids = Friendship.objects.filter(user=request.user).values_list('friend_id', flat=True)
        friends = User.objects.filter(id__in=friend_ids)
        
        serializer = FriendUserSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # افزودن دوست جدید
    def post(self, request):
        serializer = AddFriendSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            target_username = serializer.validated_data['username']
            target_user = get_object_or_404(User, username=target_username)
            
            if Friendship.objects.filter(user=request.user, friend=target_user).exists():
                return Response(
                    {"username": ["این کاربر قبلاً در لیست دوستان شما قرار دارد."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
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


# -------------------------------------------------------------
# 🌟 بخش‌های جدید مربوط به مشاوران
# -------------------------------------------------------------

# ۴. دریافت لیست مشاوران (همراه امتیازها و سوابق)
class ConsultantListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConsultantListSerializer

    def get_queryset(self):
        # دریافت کاربرانی که پروفایل مشاور دارند
        return User.objects.filter(consultant_profile__isnull=False)


# ۵. انتخاب یک مشاور توسط دانش‌آموز
class SelectConsultantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, consultant_id):
        try:
            consultant_profile = ConsultantProfile.objects.get(id=consultant_id)
            student_profile = request.user.student_profile
            
            student_profile.consultant = consultant_profile
            student_profile.save()

            return Response(
                {"message": f"مشاور {consultant_profile.user.get_full_name() or consultant_profile.user.username} با موفقیت انتخاب شد."},
                status=status.HTTP_200_OK
            )
        except ConsultantProfile.DoesNotExist:
            return Response({"error": "مشاور مورد نظر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        except StudentProfile.DoesNotExist:
            return Response({"error": "حساب کاربری شما از نوع دانش‌آموز نیست."}, status=status.HTTP_400_BAD_REQUEST)


# ۶. ثبت یا ویرایش امتیاز دانش‌آموز به مشاور (۱ تا ۵ ستاره)
class RateConsultantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, consultant_id):
        score = request.data.get('score')
        comment = request.data.get('comment', '')

        if not score or not (1 <= int(score) <= 5):
            return Response({"error": "امتیاز باید عددی بین ۱ تا ۵ باشد."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            consultant_profile = ConsultantProfile.objects.get(id=consultant_id)
            
            rating, created = ConsultantRating.objects.update_or_create(
                student=request.user,
                consultant=consultant_profile,
                defaults={'score': score, 'comment': comment}
            )

            msg = "امتیاز با موفقیت ثبت شد." if created else "امتیاز شما به‌روزرسانی شد."
            return Response(
                {
                    "message": msg, 
                    "new_average_rating": consultant_profile.average_rating
                }, 
                status=status.HTTP_200_OK
            )

        except ConsultantProfile.DoesNotExist:
            return Response({"error": "مشاور مورد نظر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)


# ۷. لیست دانش‌آموزانِ یک مشاور (مخصوص صفحه مشاوران)
class ConsultantStudentsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'consultant_profile'):
            return Response({"error": "شما به عنوان مشاور وارد نشده‌اید."}, status=status.HTTP_403_FORBIDDEN)
        
        students = StudentProfile.objects.filter(consultant=request.user.consultant_profile)
        students_data = [
            {
                "id": s.user.id,
                "username": s.user.username,
                "full_name": s.user.get_full_name() or s.user.username,
                "avatar": request.build_absolute_uri(s.avatar.url) if s.avatar else None,
                "field": s.field,
                "parent_phone": s.parent_phone,
            }
            for s in students
        ]
        return Response(students_data, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



class ConsultantListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        consultants = ConsultantProfile.objects.all()
        serializer = ConsultantListSerializer(consultants, many=True)
        return Response(serializer.data)

# ۲. انتخاب مشاور توسط دانش‌آموز
class SelectConsultantView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        consultant_id = request.data.get('consultant_id')
        try:
            student_profile = request.user.student_profile
            consultant = ConsultantProfile.objects.get(id=consultant_id)
            
            # ثبت مشاور برای دانش‌آموز
            student_profile.consultant = consultant
            student_profile.save()
            
            return Response({"message": "مشاور با موفقیت انتخاب شد"}, status=status.HTTP_200_OK)
        except StudentProfile.DoesNotExist:
            return Response({"error": "پروفایل دانش‌آموز یافت نشد"}, status=status.HTTP_400_BAD_REQUEST)
        except ConsultantProfile.DoesNotExist:
            return Response({"error": "مشاور مورد نظر یافت نشد"}, status=status.HTTP_404_NOT_FOUND)


class UploadStudentTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            student_profile = request.user.student_profile
            consultant = student_profile.consultant
            if not consultant:
                return Response({"error": "شما مشاور فعال ندارید."}, status=400)
            
            file_obj = request.FILES.get('file')
            description = request.data.get('description', '')

            task = StudentTaskFile.objects.create(
                student=request.user,
                consultant=consultant.user,
                file=file_obj,
                description=description
            )
            return Response({"message": "فایل با موفقیت ارسال شد."}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

# ۲. دریافت لیست دانش‌آموزانِ مشاور + فایل‌های هر کدام
class ConsultantStudentsTasksView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        students = StudentProfile.objects.filter(consultant__user=request.user)
        data = []
        for s in students:
            files = StudentTaskFile.objects.filter(student=s.user, consultant=request.user).order_by('-created_at')
            files_data = [{
                'id': f.id,
                'file_url': request.build_absolute_uri(f.file.url),
                'file_name': f.file.name.split('/')[-1],
                'description': f.description,
                'created_at': f.created_at.strftime('%Y-%m-%d %H:%M')
            } for f in files]

            data.append({
                'student_id': s.user.id,
                'student_name': f"{s.user.first_name} {s.user.last_name}".strip() or s.user.username,
                'field': s.field,
                'files': files_data
            })
        return Response(data)