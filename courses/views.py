from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Course
from .serializers import CourseSerializer

class CourseListAPIView(ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]