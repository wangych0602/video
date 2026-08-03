from rest_framework.routers import DefaultRouter
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet)
router.register('teacher-profiles', views.TeacherProfileViewSet)

urlpatterns = router.urls + [
    path('auth/login/', csrf_exempt(views.LoginView.as_view())),
]

urlpatterns += [
    path('teachers/', views.TeacherListView.as_view()),
]
