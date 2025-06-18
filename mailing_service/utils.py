from django.urls import reverse
from django.core.cache import cache


def get_categorized_features():
    """
    Возвращает список функций сайта, сгруппированных по категориям.
    Использует низкоуровневое кеширование.
    """
    cache_key = 'categorized_features_list'
    features = cache.get(cache_key)

    if features is None:
        features = {
            'Управление пользователями': [
                {'name': 'Мой профиль', 'url_name': 'users:profile',
                 'description': 'Просмотр и редактирование личных данных.'},
                {'name': 'Вход', 'url_name': 'users:login', 'description': 'Войти в систему.'},
                {'name': 'Регистрация', 'url_name': 'users:register', 'description': 'Создать новый аккаунт.'},
                {'name': 'Список пользователей (только для персонала)', 'url_name': 'users:user_list',
                 'description': 'Управление пользователями системы.', 'staff_only': True},
            ],
            'Операции с рассылками': [
                {'name': 'Список рассылок', 'url_name': 'mailings', 'description': 'Просмотр всех рассылок.'},
                {'name': 'Создать рассылку', 'url_name': 'create_mailing', 'description': 'Создать новую рассылку.'},
                {'name': 'Список сообщений', 'url_name': 'messages',
                 'description': 'Просмотр и управление шаблонами сообщений.'},
                {'name': 'Добавить сообщение', 'url_name': 'add_message',
                 'description': 'Создать новый шаблон сообщения.'},
                {'name': 'Список получателей', 'url_name': 'clients',
                 'description': 'Просмотр и управление списком получателей.'},
                {'name': 'Добавить получателя', 'url_name': 'add_recipient',
                 'description': 'Добавить нового получателя в базу.'},
                {'name': 'Попытки рассылок', 'url_name': 'mailing_attempts',
                 'description': 'Просмотр истории попыток отправки рассылок.'},
            ],
            'Общие функции': [
                {'name': 'Главная страница', 'url_name': 'home', 'description': 'Вернуться на главную страницу.'},
                {'name': 'Контакты', 'url_name': 'contacts',
                 'description': 'Контактная информация и форма обратной связи.'},
            ],
        }

        # Генерируем URL-адреса
        for category, items in features.items():
            for item in items:
                try:
                    item['url'] = reverse(item['url_name'])
                except Exception:
                    item['url'] = '#'  # Если URL не найден, используем заглушку

        cache.set(cache_key, features, 60 * 5)  # Кешируем на 5 минут
    return features
