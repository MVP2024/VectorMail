from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields.files import ImageFieldFile


class UserProfileForm(forms.ModelForm):
    """
        Форма для редактирования профиля пользователя.
        Включает поля: имя, фамилия, отчество, дата рождения, email, телефон, аватар, страна.
        Реализует валидацию формата и размера аватара.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'patronymic', 'birth_date', 'email', 'phone_number', 'avatar', 'country']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Страна'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')

        # Если поле аватара пустое (например, пользователь удалил аватар или не загружал его)
        if not avatar:
            return avatar

        # Если загружен новый файл (avatar является объектом UploadedFile)
        if isinstance(avatar, UploadedFile):
            # Валидация формата файла
            valid_content_types = ['image/jpeg', 'image/png', 'image/gif']
            if avatar.content_type not in valid_content_types:
                raise forms.ValidationError("Поддерживаются только изображения форматов JPEG, PNG или GIF.")
            # Валидация размера файла (5 МБ макс)
            max_size = 5 * 1024 * 1024  # 5 MB
            if avatar.size > max_size:
                raise forms.ValidationError(f"Размер файла не должен превышать {max_size / (1024 * 1024):.0f} МБ.")
        elif isinstance(avatar, ImageFieldFile):
            pass  # Ничего не делаем, просто возвращаем существующий объект

        return avatar

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'avatar' and isinstance(field.widget,
                                                     (forms.TextInput, forms.EmailInput, forms.DateInput)):
                field.widget.attrs.setdefault('class', 'form-control')


class UserRegisterForm(UserCreationForm):
    """
        Форма регистрации пользователя.
        Расширяет стандартную форму регистрации дополнительными полями профиля.
        Применяет класс 'form-control' ко всем полям, кроме паролей.
    """
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'email@example.com'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'email', 'first_name', 'last_name', 'patronymic', 'birth_date', 'phone_number', 'avatar', 'country'
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Страна'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Применяем класс 'form-control' ко всем полям, кроме паролей
        for field_name, field in self.fields.items():
            if field_name not in ['password', 'password2'] and isinstance(field.widget, (
                    forms.TextInput, forms.EmailInput, forms.DateInput, forms.FileInput
            )):
                field.widget.attrs.setdefault('class', 'form-control')


class UserLoginForm(AuthenticationForm):
    """
        Форма входа в систему.
        Настроена с кастомными placeholder'ами и классами для полей ввода.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))
