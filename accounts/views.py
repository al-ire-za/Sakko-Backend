from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView

# ایمپورت مدل‌ها
from .models import (
    Friendship, 
    ConsultantProfile, 
    ConsultantRating, 
    StudentProfile, 
    StudentTaskFile, 
    ConsultantProgram
)

# ایمپورت سریالایزرها
from .serializers import (
    RegisterSerializer, 
    UserProfileSerializer, 
    FriendUserSerializer, 
    AddFriendSerializer,
    ConsultantListSerializer,
    ConsultantRatingSerializer,
    StudentTaskFileSerializer,
    ConsultantProgramSerializer,
    CustomTokenObtainPairSerializer
)

User = get_user_model()


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


# ۳. مدیریت دوستان
class FriendListAddView(APIView):
    permission_classes = [IsAuthenticated]

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


# ۴. دریافت لیست مشاوران (همراه امتیازها و سوابق)
class ConsultantListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        consultants = ConsultantProfile.objects.all()
        serializer = ConsultantListSerializer(consultants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ۵. انتخاب مشاور توسط دانش‌آموز
class SelectConsultantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, consultant_id=None):
        # پشتیبانی از دریافت ID مشاور چه از آدرس (URL) چه از Body
        c_id = consultant_id or request.data.get('consultant_id')
        if not c_id:
            return Response({"error": "شناسه مشاور ارسال نشده است."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student_profile = request.user.student_profile
            consultant = ConsultantProfile.objects.get(id=c_id)
            
            student_profile.consultant = consultant
            student_profile.save()
            
            return Response({"message": f"مشاور {consultant.user.get_full_name() or consultant.user.username} با موفقیت انتخاب شد."}, status=status.HTTP_200_OK)
        except StudentProfile.DoesNotExist:
            return Response({"error": "پروفایل دانش‌آموز یافت نشد."}, status=status.HTTP_400_BAD_REQUEST)
        except ConsultantProfile.DoesNotExist:
            return Response({"error": "مشاور مورد نظر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)


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


# ۷. لیست دانش‌آموزانِ یک مشاور
class ConsultantStudentsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ✅ بررسی وجود رابطه مشاور
        if not hasattr(request.user, 'consultant_profile') and not hasattr(request.user, 'consultantprofile'):
            return Response({"error": "شما به عنوان مشاور وارد نشده‌اید."}, status=status.HTTP_403_FORBIDDEN)
        
        consultant_prof = getattr(request.user, 'consultant_profile', None) or getattr(request.user, 'consultantprofile', None)
        students = StudentProfile.objects.filter(consultant=consultant_prof)
        
        students_data = [
            {
                "id": s.user.id,
                "username": s.user.username,
                "full_name": s.user.get_full_name() or s.user.username,
                "avatar": request.build_absolute_uri(s.avatar.url) if hasattr(s, 'avatar') and s.avatar else None,
                "field": s.field,
                "parent_phone": s.parent_phone,
            }
            for s in students
        ]
        return Response(students_data, status=status.HTTP_200_OK)


# ۸. توکن لاگین سفارشی
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ۹. آپلود تکلیف توسط دانش‌آموز
class UploadStudentTaskView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            student_profile = request.user.student_profile
            consultant = student_profile.consultant
            if not consultant:
                return Response({"error": "شما مشاور فعال ندارید."}, status=status.HTTP_400_BAD_REQUEST)
            
            file_obj = request.FILES.get('file')
            description = request.data.get('description', '')

            if not file_obj:
                return Response({"error": "لطفاً فایل را انتخاب کنید."}, status=status.HTTP_400_BAD_REQUEST)

            task = StudentTaskFile.objects.create(
                student=request.user,
                consultant=consultant.user,
                file=file_obj,
                description=description
            )
            return Response({"message": "فایل با موفقیت ارسال شد."}, status=status.HTTP_201_CREATED)
        except StudentProfile.DoesNotExist:
            return Response({"error": "پروفایل دانش‌آموز یافت نشد."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ۱۰. دریافت تکالیف ارسال شده دانش‌آموزان به مشاور
class ConsultantStudentsTasksView(APIView):
    permission_classes = [IsAuthenticated]

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
                'created_at': f.created_at.strftime('%Y-%m-%d %H:%M') if hasattr(f, 'created_at') and f.created_at else ''
            } for f in files]

            data.append({
                'student_id': s.user.id,
                'student_name': f"{s.user.first_name} {s.user.last_name}".strip() or s.user.username,
                'field': s.field,
                'files': files_data
            })
        return Response(data, status=status.HTTP_200_OK)


# ۱۱. ارسال برنامه هفتگی توسط مشاور به دانش‌آموز
class SendProgramView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser) # 👈 لازم برای دریافت فایل

    def get(self, request):
        is_consultant = hasattr(request.user, 'consultant_profile') or hasattr(request.user, 'consultantprofile')
        if not is_consultant:
            return Response({"detail": "شما دسترسی مشاور ندارید."}, status=status.HTTP_403_FORBIDDEN)

        programs = ConsultantProgram.objects.filter(consultant=request.user).order_by('-id')
        serializer = ConsultantProgramSerializer(programs, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # ✅ پشتیبانی کامل از هر دو حالت نام‌گذاری رابطه در دیتابیس (consultant_profile یا consultantprofile)
        is_consultant = hasattr(request.user, 'consultant_profile') or hasattr(request.user, 'consultantprofile')
        
        if not is_consultant:
            return Response(
                {"detail": "شما دسترسی مشاور ندارید."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        student_id = request.data.get("student_id")
        title = request.data.get("title")
        description = request.data.get("description", "")
        file_obj = request.FILES.get("file")

        if not student_id or not title or not file_obj:
            return Response(
                {"detail": "لطفاً دانش‌آموز، عنوان و فایل برنامه را ارسال کنید."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            student = User.objects.get(id=student_id)
        except User.DoesNotExist:
            return Response({"detail": "دانش‌آموز یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        program = ConsultantProgram.objects.create(
            consultant=request.user,
            student=student,
            title=title,
            description=description,
            file=file_obj
        )

        return Response(
            {"detail": "برنامه با موفقیت ارسال شد.", "id": program.id},
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, program_id=None):
        # ۱. بررسی دسترسی مشاور
        is_consultant = hasattr(request.user, 'consultant_profile') or hasattr(request.user, 'consultantprofile')
        if not is_consultant:
            return Response({"detail": "شما دسترسی مشاور ندارید."}, status=status.HTTP_403_FORBIDDEN)

        # ۲. اگر ID از query string یا body ارسال شده بود
        if not program_id:
            program_id = request.data.get("program_id") or request.query_params.get("program_id")

        if not program_id:
            return Response({"detail": "شناسه برنامه ارسال نشده است."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # ۳. یافتن برنامه (فقط برنامه‌هایی که خود این مشاور ارسال کرده)
            program = ConsultantProgram.objects.get(id=program_id, consultant=request.user)
            
            # (اختیاری) حذف فایل فیزیکی از حافظه
            if program.file:
                program.file.delete(save=False)
                
            program.delete()
            return Response({"detail": "برنامه با موفقیت حذف شد."}, status=status.HTTP_200_OK)

        except ConsultantProgram.DoesNotExist:
            return Response({"detail": "برنامه یافت نشد یا شما مجاز به حذف آن نیستید."}, status=status.HTTP_404_NOT_FOUND)


# ۱۲. دریافت برنامه‌های هفتگی توسط دانش‌آموز
class MyProgramsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        programs = ConsultantProgram.objects.filter(student=request.user).order_by('-id')
        serializer = ConsultantProgramSerializer(programs, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)