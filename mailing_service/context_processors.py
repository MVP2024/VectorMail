from .models import Mailing, Recipient, MailingAttempt
from django.core.cache import cache


def mailing_counts(request):
    """
    Функция добавляет в контекст количества рассылок и получателей для главной страницы.
    Данные фильтруются по текущему авторизованному пользователю.
    Менеджеры видят общую статистику, обычные пользователи - только свою.
    """
    if request.user.is_authenticated:
        user = request.user
        # Определяем ключ кеша в зависимости от пользователя
        if user.is_staff:
            cache_key = 'global_mailing_counts'
        else:
            cache_key = f'user_mailing_counts_{user.pk}'

        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data
        else:
            if user.is_staff:
                # Менеджеры видят статистику по всем рассылкам и получателям
                all_mailings_count = Mailing.objects.count()
                active_mailings_count = Mailing.objects.filter(status=Mailing.STATUS_RUNNING).count()
                unique_recipients_count = Recipient.objects.distinct().count()

                successful_attempts_count = MailingAttempt.objects.filter(status=MailingAttempt.STATUS_SUCCESS).count()
                failed_attempts_count = MailingAttempt.objects.filter(status=MailingAttempt.STATUS_FAILED).count()
                total_attempts_count = MailingAttempt.objects.count()
            else:
                # Обычные пользователи видят статистику только по своим рассылкам и получателям
                user_mailings = Mailing.objects.filter(owner=user)
                user_recipients = Recipient.objects.filter(owner=user)

                all_mailings_count = user_mailings.count()
                active_mailings_count = user_mailings.filter(status=Mailing.STATUS_RUNNING).count()
                unique_recipients_count = user_recipients.distinct().count()

                user_attempts = MailingAttempt.objects.filter(mailing__owner=user)
                successful_attempts_count = user_attempts.filter(status=MailingAttempt.STATUS_SUCCESS).count()
                failed_attempts_count = user_attempts.filter(status=MailingAttempt.STATUS_FAILED).count()
                total_attempts_count = user_attempts.count()
    else:
        # Для неавторизованных пользователей всегда 0
        all_mailings_count = 0
        active_mailings_count = 0
        unique_recipients_count = 0
        successful_attempts_count = 0
        failed_attempts_count = 0
        total_attempts_count = 0

    context_data = {
        'all_mailings_count': all_mailings_count,
        'active_mailings_count': active_mailings_count,
        'unique_recipients_count': unique_recipients_count,
        'successful_attempts_count': successful_attempts_count,
        'failed_attempts_count': failed_attempts_count,
        'total_attempts_count': total_attempts_count,
    }
    return context_data
