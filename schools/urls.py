from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('buildings', views.BuildingViewSet)
router.register('schools', views.SchoolViewSet)

urlpatterns = router.urls
