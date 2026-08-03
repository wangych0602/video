from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('videos', views.VideoViewSet)
router.register('video-categories', views.VideoCategoryViewSet)
router.register('video-albums', views.VideoAlbumViewSet)

from django.urls import path
urlpatterns = router.urls + [
    path('studio/search/', views.StudioSearchView.as_view()),
    path('site-settings/', views.SiteSettingsView.as_view()),
]
