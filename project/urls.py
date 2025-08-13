from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import Home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', Home.as_view(), name='home'),
    path('core/', include('core.urls')),
    path('qa/', include('questions.urls')),
    path('notifications/', include('user_notifications.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
