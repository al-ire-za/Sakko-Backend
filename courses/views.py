from rest_framework.generics import ListCreateAPIView
from .models import Course
from .serializers import CourseSerializer

class CourseListAPIView(ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer