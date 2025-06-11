# mailing_service/models.py
from django.db import models

class Client(models.Model):
    """
    Модель для получателей рассылки (клиентов).
    """
    email = models.EmailField(unique=True, verbose_name="Email")
    fio = models.CharField(max_length=255, verbose_name="Ф.И.О.")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылки"

    def __str__(self):
        return self.email

class Message(models.Model):
    """
    Модель для сообщений, используемых в рассылках.
    """
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

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
    recipients = models.ManyToManyField(Client, verbose_name="Получатели")

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return f"Рассылка от {self.first_send_datetime.strftime('%Y-%m-%d %H:%M')}"