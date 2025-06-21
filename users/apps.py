from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
        Конфигурация приложения 'users'. Определяет настройки приложения,
        включая тип автоинкрементного поля.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
