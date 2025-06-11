from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings
from mailing_service.models import Mailing

class Command(BaseCommand):
    help = 'Sends a specific mailing by its ID.'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='The ID of the mailing to send.')

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']

        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            raise CommandError(f'Mailing with ID "{mailing_id}" does not exist.')

        if not mailing.recipients.exists():
            self.stdout.write(self.style.WARNING(f'Mailing ID {mailing_id} has no recipients. No emails sent.'))
            return

        self.stdout.write(self.style.SUCCESS(f'Attempting to send mailing ID {mailing_id} ("{mailing.message.subject}") to {mailing.recipients.count()} recipients...'))

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
                self.stdout.write(self.style.SUCCESS(f'Successfully sent to {recipient.email}'))
                sent_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to send to {recipient.email}: {e}'))
                failed_count += 1

        self.stdout.write(self.style.SUCCESS(f'Mailing ID {mailing_id} sending complete. Sent: {sent_count}, Failed: {failed_count}.'))

        # Update mailing status to 'Запущена' if it was 'Создана'
        if mailing.status == Mailing.STATUS_CREATED:
            mailing.status = Mailing.STATUS_RUNNING
            mailing.save()
            self.stdout.write(self.style.SUCCESS(f'Mailing ID {mailing_id} status updated to "{Mailing.STATUS_RUNNING}".'))