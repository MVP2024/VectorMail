from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields.files import ImageFieldFile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'patronymic', 'birth_date', 'email', 'phone_number', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')

        # Если поле аватара пустое (например, пользователь удалил аватар или не загружал его)
        if not avatar:
            return avatar

        # Если загружен новый файл (avatar является объектом UploadedFile)
        if isinstance(avatar, UploadedFile):
            # Валидация формата файла
            valid_content_types = ['image/jpeg', 'image/png', 'image/gif']  # Добавил GIF
            if avatar.content_type not in valid_content_types:
                raise forms.ValidationError("Поддерживаются только изображения форматов JPEG, PNG или GIF.")
            # Валидация размера файла (5 МБ макс)
            max_size = 5 * 1024 * 1024  # 5 MB
            if avatar.size > max_size:
                raise forms.ValidationError(f"Размер файла не должен превышать {max_size / (1024 * 1024):.0f} МБ.")
        # Если это существующий объект ImageFieldFile (новый файл не загружен, но был существующий)
        # В этом случае валидация content_type или размера не требуется.
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
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'email@example.com'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
        'email', 'first_name', 'last_name', 'patronymic', 'birth_date', 'phone_number', 'avatar')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Применяем класс 'form-control' ко всем полям, кроме паролей
        for field_name, field in self.fields.items():
            if field_name not in ['password', 'password2'] and isinstance(field.widget, (
            forms.TextInput, forms.EmailInput, forms.DateInput, forms.FileInput)):
                field.widget.attrs.setdefault('class', 'form-control')


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))
