from django.urls import path
from .views import CourseListAPIView

urlpatterns = [
    path('', CourseListAPIView.as_view(), name='course-list'),
]