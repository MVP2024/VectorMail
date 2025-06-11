from django.core.management import call_command
from django.core.management.base import BaseCommand

from mailing_service.models import Client, Message, Mailing


class Command(BaseCommand):
    help = "Загружает тестовые данные из фикстуры после очистки существующих данных для mailing_service"

    def handle(self, *args, **options):
        self.stdout.write("Удаление существующих данных из mailing_service...")
        # Удаляем данные из моделей Mailing, Message и Client
        # Важно удалять в правильном порядке из-за внешних ключей
        Mailing.objects.all().delete()
        Message.objects.all().delete()
        Client.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Существующие данные mailing_service удалены."))

        self.stdout.write("Загрузка данных из фикстуры initial_data.json...")
        # Загружаем данные из фикстуры
        call_command("loaddata", "initial_data.json")
        self.stdout.write(self.style.SUCCESS("Данные успешно загружены."))