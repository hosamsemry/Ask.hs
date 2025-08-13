from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import Home
from debug_view import debug_s3_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', Home.as_view(), name='home'),
    path('core/', include('core.urls')),
    path('qa/', include('questions.urls')),
    path('notifications/', include('user_notifications.urls')),
    path('debug-s3/', debug_s3_view, name='debug_s3'),  # Temporary debug view
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
