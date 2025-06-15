from django.urls import path
from .views import (
    home_view, RecipientListView, RecipientFormView, RecipientDeleteView,
    MessageListView, MessageDetailView, MessageCreateUpdateView, MessageDeleteView,
    MailingListView, MailingCreateUpdateView, MailingDeleteView,
    FilteredMailingListView, MailingAttemptListView, send_mailing_view, contacts_view, toggle_mailing_status,
    send_single_mailing, feature_list_view
)
from .models import Mailing

urlpatterns = [
    path('', home_view, name='home'),
    path('clients/', RecipientListView.as_view(), name='clients'),
    path('clients/add/', RecipientFormView.as_view(), name='add_recipient'),
    path('clients/edit/<int:pk>/', RecipientFormView.as_view(), name='edit_recipient'),
    path('clients/delete/<int:pk>/', RecipientDeleteView.as_view(), name='delete_recipient'),

    path('messages/', MessageListView.as_view(), name='messages'),
    path('messages/add/', MessageCreateUpdateView.as_view(), name='add_message'),
    path('messages/detail/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('messages/edit/<int:pk>/', MessageCreateUpdateView.as_view(), name='edit_message'),
    path('messages/delete/<int:pk>/', MessageDeleteView.as_view(), name='delete_message'),

    path('mailings/', MailingListView.as_view(), name='mailings'),  # Для всех рассылок
    path('mailings/created/', FilteredMailingListView.as_view(status_filter=Mailing.STATUS_CREATED),
         name='mailings_created'),
    path('mailings/running/', FilteredMailingListView.as_view(status_filter=Mailing.STATUS_RUNNING),
         name='mailings_running'),
    path('mailings/completed/', FilteredMailingListView.as_view(status_filter=Mailing.STATUS_COMPLETED),
         name='mailings_completed'),
    path('mailings/create/', MailingCreateUpdateView.as_view(), name='create_mailing'),
    path('mailings/edit/<int:pk>/', MailingCreateUpdateView.as_view(), name='edit_mailing'),
    path('mailings/delete/<int:pk>/', MailingDeleteView.as_view(), name='delete_mailing'),
    path('mailings/<int:pk>/toggle_status/', toggle_mailing_status, name='toggle_mailing_status'),
    path('mailings/<int:pk>/send/', send_single_mailing, name='send_single_mailing'),

    path('mailing_attempts/', MailingAttemptListView.as_view(), name='mailing_attempts'),
    path('send_mailing/', send_mailing_view, name='send_mailing'),
    path('contacts/', contacts_view, name='contacts'),
    path('features/', feature_list_view, name='feature_list'),
]
