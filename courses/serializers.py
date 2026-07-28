from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 
                  'title',
                'description', 
                'instructor', 
                'created_at',
                'icon_name', 
                'dark_color', 
                'light_color',]