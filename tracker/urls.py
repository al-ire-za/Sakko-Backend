from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, StudySessionViewSet, SleepLogViewSet, LeaderboardView

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'study-sessions', StudySessionViewSet, basename='studysession'),
router.register(r'sleep-logs', SleepLogViewSet, basename='sleeplog')

urlpatterns = [
    path('', include(router.urls)),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    
]