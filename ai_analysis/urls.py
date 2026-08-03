from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClassAnalysisTaskViewSet,
    AIAnalysisResultViewSet,
    AIModelConfigViewSet,
)

router = DefaultRouter()
router.register(r'tasks', ClassAnalysisTaskViewSet, basename='analysis-task')
router.register(r'results', AIAnalysisResultViewSet, basename='analysis-result')
router.register(r'config', AIModelConfigViewSet, basename='ai-model-config')

urlpatterns = [
    path('', include(router.urls)),
]