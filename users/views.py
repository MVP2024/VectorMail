from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UserProfileForm, UserRegisterForm, UserLoginForm
from .models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login


class StaffRequiredMixin(AccessMixin):
    """
    Миксин, который проверяет, является ли пользователь персоналом (is_staff=True).
    Если нет, перенаправляет на главную страницу с сообщением об ошибке.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            messages.error(request, "У вас нет прав доступа к этой странице.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        return super().form_valid(form)


class RegisterUserView(CreateView):
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login') # Это будет переопределено методом form_valid

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # Деактивировать учетную запись до подтверждения email
        user.save()

        current_site = get_current_site(self.request)
        mail_subject = 'Активируйте ваш аккаунт VectorMail'
        message = render_to_string('users/email/account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        send_mail(mail_subject, message, None, [user.email])  # from_email задан в settings.py
        messages.success(self.request,
                         'Пожалуйста, подтвердите ваш email для завершения регистрации. Мы отправили вам письмо с инструкциями.')
        return redirect('users:account_activation_sent')

class LoginUserView(LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('home') # Перенаправляем на главную после успешного входа

class LogoutUserView(LogoutView):
    next_page = reverse_lazy('users:login') # Перенаправляем на страницу входа после выхода


# Функциональное представление для активации аккаунта
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user) # Вход в систему пользователя после активации
        messages.success(request, 'Ваш аккаунт успешно активирован! Вы вошли в систему.')
        return redirect('home') # Перенаправляем на домашнюю страницу или страницу профиля
    else:
        messages.error(request, 'Ссылка активации недействительна или срок ее действия истек.')
        return redirect('users:account_activation_invalid')


class UserListView(StaffRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    ordering = ['username']  # Сортировка пользователей по имени


class ToggleUserActiveStatusView(StaffRequiredMixin, View):

    def post(self, request, pk):
        user_to_toggle = get_object_or_404(User, pk=pk)

        if user_to_toggle == request.user:
            messages.error(request, "Вы не можете заблокировать или разблокировать свой собственный аккаунт.")
        else:
            user_to_toggle.is_active = not user_to_toggle.is_active
            user_to_toggle.save()
            status_message = "заблокирован" if not user_to_toggle.is_active else "разблокирован"
            messages.success(request, f"Пользователь '{user_to_toggle.username}' успешно {status_message}.")

        return redirect('users:user_list')