"""
URL configuration for video_platform project.

The urlpatterns list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from video_platform.health import health

urlpatterns = [
    path('health/', health, name='health'),
    path('', RedirectView.as_view(url='http://127.0.0.1:5173/')),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/', include('users.urls')),
    path('api/', include('schools.urls')),
    path('api/', include('videos.urls')),
    path('api/', include('devices.urls')),
    path('api/', include('live.urls')),
    path('api/', include('reviews.urls')),
    path('api/', include('system.urls')),
    path('api/ai/', include('ai_analysis.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)