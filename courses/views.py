from rest_framework.generics import ListCreateAPIView
from .models import Course
from .serializers import CourseSerializer
from rest_framework.permissions import IsAuthenticated

class CourseListAPIView(ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]