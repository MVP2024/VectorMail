from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings
from mailing_service.models import Mailing, MailingAttempt


class Command(BaseCommand):
    help = 'Отправляет конкретную рассылку по её ID.'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки для отправки.')

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']

        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            raise CommandError(f'Рассылка с ID "{mailing_id}" не существует.')

        if not mailing.recipients.exists():
            self.stdout.write(
                self.style.WARNING(f'Рассылка с ID {mailing_id} не имеет получателей. Письма не отправлены.'))
            return

        self.stdout.write(self.style.SUCCESS(
            f'Попытка отправить рассылку с ID {mailing_id} ("{mailing.message.subject}") '
            f'{mailing.recipients.count()} получателям...'))

        sent_count = 0
        failed_count = 0
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')

        for recipient in mailing.recipients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=from_email,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                # Создаем запись об успешной попытке рассылки
                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status=MailingAttempt.STATUS_SUCCESS,
                    error_message=""
                )
                self.stdout.write(self.style.SUCCESS(f'Успешно отправлено на {recipient.email}'))
                sent_count += 1
            except Exception as e:
                # Создаем запись о неуспешной попытке рассылки
                error_detail = str(e)
                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status=MailingAttempt.STATUS_FAILED,  # Используем STATUS_FAILED
                    error_message=error_detail
                )
                self.stdout.write(self.style.ERROR(f'Не удалось отправить на {recipient.email}: {e}'))
                failed_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Отправка рассылки с ID {mailing_id} завершена. Отправлено: {sent_count}, Ошибок: {failed_count}.'))

        # Update mailing status to 'Завершена' if it was 'Создана' or 'Запущена'
        # Логика обновления статуса рассылки после ручной отправки
        if mailing.status != Mailing.STATUS_COMPLETED:  # Проверяем, что рассылка еще не завершена
            mailing.status = Mailing.STATUS_COMPLETED  # Устанавливаем статус "Завершена"
            mailing.save()
            self.stdout.write(
                self.style.SUCCESS(f'Статус рассылки с ID {mailing_id} обновлен на "{Mailing.STATUS_COMPLETED}".'))
