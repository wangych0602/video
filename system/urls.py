from django.urls import path
from . import views

urlpatterns = [
    path('site-config/', views.SiteConfigView.as_view(), name='site-config'),
]