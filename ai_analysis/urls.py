from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClassAnalysisTaskViewSet,
    AIAnalysisResultViewSet,
    AIModelConfigViewSet,
    ProviderStatusView,
    UsageStatisticsView,
    AvailableModelsView,
)

router = DefaultRouter()
router.register(r'tasks', ClassAnalysisTaskViewSet, basename='analysis-task')
router.register(r'results', AIAnalysisResultViewSet, basename='analysis-result')
router.register(r'config', AIModelConfigViewSet, basename='ai-model-config')

urlpatterns = [
    path('', include(router.urls)),

    # Provider 状态
    path('providers/status/', ProviderStatusView.as_view(), name='provider-status'),
    
    # 使用统计
    path('usage/statistics/', UsageStatisticsView.as_view(), name='usage-statistics'),
    
    # 可用模型
    path('models/available/', AvailableModelsView.as_view(), name='available-models'),

]