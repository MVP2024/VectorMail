
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mailings/', include('mailing_service.urls')),
path('', RedirectView.as_view(url='/mailings/send/', permanent=False)),
]
