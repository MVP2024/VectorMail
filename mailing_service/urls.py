from django.urls import path
from .views import send_mailing_view

urlpatterns = [
    path('send/', send_mailing_view, name='send_mailing'),
]
