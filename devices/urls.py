from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('devices', views.DeviceViewSet)
router.register('live-sessions', views.LiveSessionViewSet)

urlpatterns = router.urls
