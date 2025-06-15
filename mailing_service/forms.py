from .models import Mailing, Recipient, Message
from django import forms


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['last_name', 'first_name', 'patronymic', 'email', 'comment']
        widgets = {
            'last_name': forms.TextInput(attrs={'placeholder': 'Введите фамилию'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Введите имя'}),
            'patronymic': forms.TextInput(attrs={'placeholder': 'Введите Отчество'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Введите Email'}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.EmailInput)):
                field.widget.attrs['class'] = 'form-control'


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['message', 'recipients', 'first_send_datetime', 'end_send_datetime', 'status']
        widgets = {
            'message': forms.Select(attrs={'class': 'form-select'}),
            'recipients': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'first_send_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_send_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Получаем пользователя из kwargs
        super().__init__(*args, **kwargs)
        if user:
            # Фильтруем сообщения и получателей по текущему пользователю
            self.fields['message'].queryset = Message.objects.filter(owner=user)
            self.fields['recipients'].queryset = Recipient.objects.filter(owner=user)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.EmailInput, forms.DateTimeInput)):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs['class'] = 'form-select'


class MailingSendForm(forms.Form):
    mailing = forms.ModelChoiceField(
        queryset=Mailing.objects.none(),
        label="Выберите рассылку для отправки",
        empty_label="--- Выберите рассылку ---",
        widget=forms.Select(attrs={'class': 'form-select'})  # Добавляем класс для стилизации
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Фильтруем рассылки по владельцу
            self.fields['mailing'].queryset = Mailing.objects.filter(owner=user)


class MessageForm(forms.ModelForm):
    FORBIDDEN_WORDS = [
        'казино', 'криптовалюта', 'крипта', 'биржа', 'дешево',
        'бесплатно', 'обман', 'полиция', 'радар'
    ]

    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Введите тему письма'}),
            'body': forms.Textarea(attrs={'rows': 10, 'placeholder': 'Введите сообщение'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea)):
                field.widget.attrs['class'] = 'form-control'

    def clean_subject(self):
        subject = self.cleaned_data['subject']
        for word in self.FORBIDDEN_WORDS:
            if word in subject.lower():
                raise forms.ValidationError(
                    f"Тема сообщения содержит запрещенное слово: '{word}'."
                )
        return subject

    def clean_body(self):
        body = self.cleaned_data['body']
        for word in self.FORBIDDEN_WORDS:
            if word in body.lower():
                raise forms.ValidationError(
                    f"Сообщение содержит запрещенное слово: '{word}'."
                )
        return body


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ваш Email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Ваше сообщение'}))
