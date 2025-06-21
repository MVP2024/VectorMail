from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing_service.models import Mailing, Message, Recipient


# Класс Command - это Django-команда для управления группами пользователей
class Command(BaseCommand):
    help = 'Создает группу "Менеджеры" и назначает ей необходимые права.'

    # Основной метод, который выполняется при запуске команды
    def handle(self, *args, **options):
        # Создает группу "Менеджеры" если она не существует
        manager_group, created = Group.objects.get_or_create(name='Менеджеры')

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" успешно создана.'))
        else:
            self.stdout.write(self.style.WARNING('Группа "Менеджеры" уже существует.'))

        # Получает типы содержимого для моделей (нужно для получения прав)
        mailing_ct = ContentType.objects.get_for_model(Mailing)
        message_ct = ContentType.objects.get_for_model(Message)
        recipient_ct = ContentType.objects.get_for_model(Recipient)

        # Список прав, которые должны быть у менеджеров
        permissions_to_add = [
            # Права на просмотр всех объектов
            'can_view_all_mailings',
            'can_view_all_messages',
            'can_view_all_recipients',
            # Права на изменение статуса рассылки
            'can_toggle_any_mailing_status',
            'can_send_any_mailing',
            # Добавьте другие права, если менеджеры должны иметь возможность редактировать/удалять чужие объекты
            # 'can_edit_all_mailings',
            # 'can_delete_all_mailings',
            # 'can_edit_all_messages',
            # 'can_delete_all_messages',
            # 'can_edit_all_recipients',
            # 'can_delete_all_recipients',
        ]

        # Проверяет и добавляет права группе
        current_permissions = manager_group.permissions.values_list('codename', flat=True)
        for perm_codename in permissions_to_add:
            if perm_codename not in current_permissions:
                try:
                    # Улучшенная логика для получения разрешения
                    permission = None
                    if 'mailing' in perm_codename:  # Проверяем на 'mailing' (единственное число)
                        permission = Permission.objects.get(content_type=mailing_ct, codename=perm_codename)
                    elif 'message' in perm_codename:
                        permission = Permission.objects.get(content_type=message_ct, codename=perm_codename)
                    elif 'recipient' in perm_codename:
                        permission = Permission.objects.get(content_type=recipient_ct, codename=perm_codename)

                    if permission:
                        manager_group.permissions.add(permission)
                        self.stdout.write(self.style.SUCCESS(f'Право "{perm_codename}" добавлено группе "Менеджеры".'))
                    else:
                        # Это сообщение будет выведено, если разрешение не соответствует ни одной модели
                        self.stdout.write(self.style.WARNING(f"Неизвестное разрешение: {perm_codename}"))
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Право "{perm_codename}" не найдено. Убедитесь, что миграции выполнены.'))
            else:
                self.stdout.write(self.style.WARNING(f'Право "{perm_codename}" уже есть у группы "Менеджеры".'))

        self.stdout.write(self.style.SUCCESS('Настройка прав для группы "Менеджеры" завершена.'))
