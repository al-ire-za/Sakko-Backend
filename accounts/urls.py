from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, UserProfileView
from .views import (
    FriendListAddView, 
    ConsultantListView, 
    SelectConsultantView, 
    RateConsultantView, 
    ConsultantStudentsListView, 
    CustomTokenObtainPairView,
    UploadStudentTaskView,         
    ConsultantStudentsTasksView,
    SendProgramView, 
    MyProgramsView 
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('friends/', FriendListAddView.as_view(), name='friends-list-add'),
    path('consultants/', ConsultantListView.as_view(), name='consultant-list'),
    path('consultants/<int:consultant_id>/select/', SelectConsultantView.as_view(), name='select-consultant'),
    path('consultants/<int:consultant_id>/rate/', RateConsultantView.as_view(), name='rate-consultant'),
    
    # 🌟 آدرس اصلاح شده برای تطابق با فرانت‌اند:
    path('consultant/students/', ConsultantStudentsListView.as_view(), name='consultant-students'),
    
    path('select-consultant/', SelectConsultantView.as_view(), name='select-consultant'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    path('upload-task/', UploadStudentTaskView.as_view(), name='upload-student-task'),
    path('consultant-students/', ConsultantStudentsTasksView.as_view(), name='consultant-students-tasks'),
    path('send-program/', SendProgramView.as_view(), name='send-program'),
    path('send-program/<int:program_id>/', SendProgramView.as_view(), name='delete-program'),
    path('my-programs/', MyProgramsView.as_view(), name='my-programs'),
]