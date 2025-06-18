from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
        Кастомная конфигурация админ-панели для модели User.
        Добавляет поля: отчество, дата рождения, телефон, аватар, страна.
        Расширяет стандартные fieldsets для формы редактирования и создания пользователя.
        Обновляет отображение списка пользователей в админке.
    """
    # Добавляем наши кастомные поля в админ-панель
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('patronymic', 'birth_date', 'phone_number', 'avatar', 'country')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('patronymic', 'birth_date', 'phone_number', 'avatar', 'country')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'patronymic', 'country', 'is_staff')
