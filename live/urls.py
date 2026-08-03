from django.urls import path
from rest_framework.routers import DefaultRouter

from devices import views as device_views
from . import views

router = DefaultRouter()
router.register('live-rooms', views.LiveRoomViewSet)

urlpatterns = router.urls + [
    path('live/callback/', device_views.LiveCallbackView.as_view()),
    path('live/personal-start/', views.PersonalLiveStartView.as_view()),
    path('live/personal-stop/', views.PersonalLiveStopView.as_view()),
    path('live/personal-delete/', views.PersonalLiveDeleteView.as_view()),
]
