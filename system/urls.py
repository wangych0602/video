from django.urls import path
from . import views

urlpatterns = [
    path('site-config/', views.SiteConfigView.as_view(), name='site-config'),
    path('system/ai-health/', views.AIHealthView.as_view(), name='ai-health'),
]
