
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    patronymic = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер телефона")
    avatar = models.ImageField(upload_to='users_avatars/', blank=True, null=True, verbose_name="Аватар")
    email = models.EmailField(unique=True, verbose_name="email address")
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Страна")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
