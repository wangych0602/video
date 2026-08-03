from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('reviews', views.ReviewViewSet)

urlpatterns = router.urls
