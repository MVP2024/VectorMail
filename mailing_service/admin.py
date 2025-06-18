from django.contrib import admin
from .models import Message, Mailing, Recipient, MailingAttempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'owner')
    search_fields = ('first_name', 'last_name', 'patronymic', 'email', "owner__username")
    list_filter = ('last_name', 'owner')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at', 'owner')
    search_fields = ('subject', 'body', 'owner__username')
    list_filter = ('owner',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('first_send_datetime', 'end_send_datetime', 'status', 'message', 'owner')
    list_filter = ('status', 'owner')
    raw_id_fields = ('message', 'recipients')  # Типа для отношений «многие ко многим»


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'recipient', 'sent_at', 'status')
    list_filter = ('status', 'sent_at')
    search_fields = ('mailing__message__subject', 'recipient__email', 'error_message')
    raw_id_fields = ('mailing', 'recipient')
