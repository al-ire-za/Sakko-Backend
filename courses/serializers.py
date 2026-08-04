from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    target_audience_display = serializers.CharField(source='get_target_audience_display', read_only=True)
    class Meta:
        model = Course
        fields = ['id', 
                  'title',
                'description', 
                'instructor', 
                'target_audience',         
                'target_audience_display',
                'created_at',
                'icon_name', 
                'dark_color', 
                'light_color',]