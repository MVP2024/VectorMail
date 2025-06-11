from django import forms
from .models import Mailing
from typing import cast
from django.db.models.query import QuerySet


class MailingSendForm(forms.Form):
    mailing = forms.ModelChoiceField(
        queryset=cast(QuerySet, Mailing.objects.all()),
        label="Выберите рассылку для отправки",
        empty_label="--- Выберите рассылку ---"
    )
