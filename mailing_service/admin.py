from django.contrib import admin
from .models import Client, Message, Mailing

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'fio')
    search_fields = ('email', 'fio')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject',)
    search_fields = ('subject',)

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('first_send_datetime', 'end_send_datetime', 'status', 'message')
    list_filter = ('status',)
    raw_id_fields = ('message', 'recipients') # Типа для отношений «многие ко многим»