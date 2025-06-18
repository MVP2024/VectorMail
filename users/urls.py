from django.urls import path, reverse_lazy
from .views import UserProfileView, RegisterUserView, LoginUserView, LogoutUserView, activate, UserListView, \
    ToggleUserActiveStatusView
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),  # URL-адрес для активации по электронной почте
    path('account_activation_sent/', TemplateView.as_view(template_name='users/email/account_activation_sent.html'),
         name='account_activation_sent'),
    path('account_activation_invalid/',
         TemplateView.as_view(template_name='users/email/account_activation_invalid.html'),
         name='account_activation_invalid'),

    # URL-адреса для восстановления пароля
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset_form.html',
        success_url=reverse_lazy('users:password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url=reverse_lazy('users:password_reset_complete')
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),

    # Новые URL-адреса для менеджеров
    path('list/', UserListView.as_view(), name='user_list'),
    path('<int:pk>/toggle_active/', ToggleUserActiveStatusView.as_view(), name='toggle_user_active_status'),
]
