from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mailing_service.urls')),  # Теперь URL-адреса из mailing_service будут доступны с корня
    path('users/', include('users.urls')),
    # Добавляем URL-адреса для сброса пароля из Django auth
    # path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
