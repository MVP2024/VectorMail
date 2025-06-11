from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import MailingSendForm
from .models import Mailing

def send_mailing_view(request):
    if request.method == 'POST':
        form = MailingSendForm(request.POST)
        if form.is_valid():
            mailing = form.cleaned_data['mailing']

            if not mailing.recipients.exists():
                messages.warning(request, f'Рассылка "{mailing.message.subject}" (ID: {mailing.id}) не имеет получателей. Письма не отправлены.')
                return redirect('send_mailing')

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
                    sent_count += 1
                except Exception as e:
                    failed_count += 1
                    messages.error(request, f'Не удалось отправить письмо на {recipient.email}: {e}')

            messages.success(request, f'Рассылка "{mailing.message.subject}" (ID: {mailing.id}) завершена. Отправлено: {sent_count}, Ошибок: {failed_count}.')

            # Изменяем статус рассылки на «Запущена», если он был «Создан»
            if mailing.status == Mailing.STATUS_CREATED:
                mailing.status = Mailing.STATUS_RUNNING
                mailing.save()
                messages.info(request, f'Статус рассылки (ID: {mailing.id}) обновлен на "{Mailing.STATUS_RUNNING}".')

            return redirect('send_mailing')
    else:
        form = MailingSendForm()

    return render(request, 'send_mailing.html', {'form': form})