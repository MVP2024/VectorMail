from django.db import models
from django.conf import settings  # Для связи с AUTH_USER_MODEL


class Recipient(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя", blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name="Фамилия", blank=True, null=True)
    patronymic = models.CharField(max_length=100, verbose_name="Отчество", blank=True, null=True)
    email = models.EmailField(unique=True, verbose_name="Email получателя")
    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец", null=True,
                              blank=True)

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name}".strip()
        display_name = f" ({full_name})" if full_name else ""

        # Добавляем часть комментария к отображению получателей в выпадающем списке
        comment_preview = ""
        if self.comment:
            truncated_comment = (self.comment[:30] + '...') if len(self.comment) > 30 else self.comment
            comment_preview = f" - {truncated_comment}"

        return f"{self.email}{display_name}{comment_preview}"

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ['last_name', 'first_name']
        permissions = [
            ("can_view_all_recipients", "Can view all recipients"),
            ("can_edit_all_recipients", "Can edit all recipients"),
            ("can_delete_all_recipients", "Can delete all recipients"),
        ]

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.patronymic]
        return " ".join(filter(None, parts))  # Фильтруем пустые строки и None


class Message(models.Model):
    """
    Модель для сообщений, используемых в рассылках.
    """
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец", null=True,
                              blank=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['-created_at']  # Сортировка по дате создания, новые сверху
        permissions = [
            ("can_view_all_messages", "Can view all messages"),
            ("can_edit_all_messages", "Can edit all messages"),
            ("can_delete_all_messages", "Can delete all messages"),
        ]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """
    Модель для управления рассылками.
    """
    STATUS_CREATED = 'created'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_CREATED, 'Создана'),
        (STATUS_RUNNING, 'Запущена'),
        (STATUS_COMPLETED, 'Завершена'),
    ]

    first_send_datetime = models.DateTimeField(verbose_name="Дата и время первой отправки")
    end_send_datetime = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name="Статус"
    )
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение")
    recipients = models.ManyToManyField(Recipient, verbose_name="Получатели")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец", null=True,
                              blank=True)

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ("can_view_all_mailings", "Can view all mailings"),
            ("can_edit_all_mailings", "Can edit all mailings"),
            ("can_delete_all_mailings", "Can delete all mailings"),
            ("can_toggle_any_mailing_status", "Can toggle status of any mailing"),
            ("can_send_any_mailing", "Can send any mailing"),
        ]

    def __str__(self):
        return f"Рассылка от {self.first_send_datetime.strftime('%Y-%m-%d %H:%M')}"


class MailingAttempt(models.Model):
    """
    Модель для записи каждой попытки отправки письма в рамках рассылки.
    """
    # STATUS_FAILURE = None
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Успешно'),
        (STATUS_FAILED, 'Ошибка'),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name="Рассылка")
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, verbose_name="Получатель")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name="Статус попытки"
    )
    error_message = models.TextField(blank=True, null=True, verbose_name="Сообщение об ошибке")

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        ordering = ['-sent_at']

    def __str__(self):
        return (f"Попытка для {self.mailing.message.subject} "
                f"получателю {self.recipient.email} ({self.get_status_display()})")
