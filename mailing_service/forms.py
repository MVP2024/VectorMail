from django import forms
from .models import Mailing

class MailingSendForm(forms.Form):
    mailing = forms.ModelChoiceField(
        queryset=Mailing.objects.all(),
        label="Выберите рассылку для отправки",
        empty_label="--- Выберите рассылку ---"
    )