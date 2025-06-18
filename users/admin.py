from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Добавляем ваши кастомные поля в админ-панель
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('patronymic', 'birth_date', 'phone_number', 'avatar', 'country')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('patronymic', 'birth_date', 'phone_number', 'avatar', 'country')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'patronymic', 'country', 'is_staff')
