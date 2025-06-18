from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from mailing_service.models import Recipient, Message, Mailing


class Command(BaseCommand):
    help = "Загружает тестовые данные из фикстуры после очистки существующих данных для mailing_service"

    def handle(self, *args, **options):
        self.stdout.write("Удаление существующих данных из mailing_service...")
        # Удаляем данные из моделей Mailing, Message, Recipient
        Mailing.objects.all().delete()
        Message.objects.all().delete()
        Recipient.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Существующие данные mailing_service удалены."))

        fixture_name = "initial_data.json"
        fixture_path = Path(settings.BASE_DIR) / 'mailing_service' / 'fixtures' / fixture_name

        if fixture_path.exists():

            self.stdout.write("Загрузка данных из фикстуры initial_data.json...")

            # Загружаем данные из фикстуры
            call_command("loaddata", "initial_data.json")
            self.stdout.write(self.style.SUCCESS("Данные успешно загружены."))

        else:
            self.stdout.write(self.style.WARNING(
                f"Файл фикстуры '{fixture_name}' не найден по пути: {fixture_path}. Данные не загружены."))
