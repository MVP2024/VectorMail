from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from .utils import get_categorized_features
from django.core.cache import cache
from .forms import MailingSendForm, RecipientForm, MailingForm, MessageForm, ContactForm
from .models import Mailing, Recipient, Message, MailingAttempt


class CustomLoginRequiredMixin(AccessMixin):
    """
    Миксин, который перенаправляет неавторизованных пользователей на главную страницу
    и показывает сообщение об отсутствии прав.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request,
                           "Для просмотра и управления сообщениями, рассылками и получателями необходимо "
                           "войти в систему или зарегистрироваться. Пожалуйста, <a href='/users/login/'>войдите</a> "
                           "или <a href='/users/register/'>зарегистрируйтесь</a>.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class OwnerRequiredMixin(AccessMixin):
    """
    Миксин, который проверяет, является ли текущий пользователь владельцем объекта.
    Если нет, перенаправляет на страницу permission_denied.html с сообщением об ошибке.
    Предполагает, что view имеет метод get_object() для получения объекта.
    Эта проверка применяется ко всем авторизованным пользователям.
    """
    permission_denied_message = "У Вас недостаточно прав для выполнения этого действия."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Если пользователь не авторизован, перенаправляем на страницу входа
            return self.handle_no_permission()

        self.object = None
        if 'pk' in kwargs:
            try:
                self.object = super().get_object()
            except self.model.DoesNotExist:
                raise  # Позволяем Django обработать 404 для несуществующих объектов
            except Exception as e:
                messages.error(request, f"Произошла ошибка при получении объекта: {e}")
                return redirect(self.get_redirect_url())

            # Если пользователь является владельцем объекта, разрешаем доступ
            if self.object and self.object.owner == request.user:
                return super().dispatch(request, *args, **kwargs)

            # Если пользователь не является владельцем, проверяем наличие специфических прав
            model_name = self.model.__name__.lower()  # Например, 'mailing', 'message', 'recipient'
            required_permission = None

            if isinstance(self, (CreateView, UpdateView)):
                required_permission = f'mailing_service.can_edit_all_{model_name}s'
            elif isinstance(self, DeleteView):
                required_permission = f'mailing_service.can_delete_all_{model_name}s'
            elif isinstance(self, DetailView):
                required_permission = f'mailing_service.can_view_all_{model_name}s'

            if required_permission and request.user.has_perm(required_permission):
                return super().dispatch(request, *args, **kwargs)
            else:
                messages.error(request, self.permission_denied_message)
                return redirect(self.get_redirect_url())

        # Для CreateView без PK, разрешаем, если пользователь авторизован
        # (он будет владельцем создаваемого объекта)
        if isinstance(self, CreateView) and 'pk' not in kwargs:
            return super().dispatch(request, *args, **kwargs)

        messages.error(request, self.permission_denied_message)
        return redirect(self.get_redirect_url())

    def get_redirect_url(self):
        return reverse_lazy('permission_denied')


@cache_page(60 * 1)  # Кешировать страницу на 1 минуту (60 секунд)
@vary_on_cookie  # Кешировать отдельно для каждого пользователя (по кукам сессии)
def home_view(request):
    return render(request, 'index.html')


class RecipientListView(CustomLoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'list_recipients.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        user = self.request.user
        # Создаем уникальный ключ кеша для каждого пользователя (или для всех, если это менеджер)
        if user.is_staff:
            cache_key = 'all_recipients_list'
        else:
            cache_key = f'user_recipients_list_{user.pk}'

        recipients_queryset = cache.get(cache_key)

        if recipients_queryset is None:
            if user.is_staff:
                # Менеджеры видят всех получателей
                recipients_queryset = super().get_queryset()
            else:
                # Обычные пользователи - только своих
                recipients_queryset = super().get_queryset().filter(owner=user)

            # Кешируем результат на 5 минут (300 секунд)
            cache.set(cache_key, recipients_queryset, 300)
        return recipients_queryset


class RecipientFormView(OwnerRequiredMixin, CustomLoginRequiredMixin, CreateView, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'add_new_recipient.html'
    success_url = reverse_lazy('clients')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_object(self, queryset=None):
        # Получаем объект по PK без фильтрации по владельцу.
        # Проверка владельца будет выполнена в OwnerRequiredMixin.
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk:
            return get_object_or_404(self.model, pk=pk)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = self.object is not None
        return context


class RecipientDeleteView(OwnerRequiredMixin, CustomLoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = 'recipient_confirm_delete.html'
    success_url = reverse_lazy('clients')

    def get_object(self, queryset=None):
        # Получаем объект по PK без фильтрации по владельцу.
        # Проверка владельца будет выполнена в OwnerRequiredMixin.
        pk = self.kwargs.get(self.pk_url_kwarg)
        return get_object_or_404(self.model, pk=pk)


class MessageListView(CustomLoginRequiredMixin, ListView):
    model = Message
    template_name = 'list_messages.html'
    context_object_name = 'messages'

    def get_queryset(self):
        user = self.request.user
        # Создаем уникальный ключ кеша для каждого пользователя (или для всех, если это менеджер)
        if user.is_staff:
            cache_key = 'all_messages_list'
        else:
            cache_key = f'user_messages_list_{user.pk}'

        messages_queryset = cache.get(cache_key)

        if messages_queryset is None:
            if user.is_staff:
                # Менеджеры видят все сообщения
                messages_queryset = super().get_queryset()
            else:
                # Обычные пользователи - только свои
                messages_queryset = super().get_queryset().filter(owner=user)

            # Кешируем результат на 5 минут (300 секунд)
            cache.set(cache_key, messages_queryset, 300)
        return messages_queryset


class MessageDetailView(OwnerRequiredMixin, CustomLoginRequiredMixin, DetailView):
    model = Message
    template_name = 'message_detail.html'
    context_object_name = 'message'

    def get_object(self, queryset=None):
        # Проверка прав владения теперь полностью обрабатывается OwnerRequiredMixin.
        # Этот метод просто извлекает объект.
        pk = self.kwargs.get(self.pk_url_kwarg)
        return get_object_or_404(self.model, pk=pk)


class MessageCreateUpdateView(OwnerRequiredMixin, CustomLoginRequiredMixin, CreateView, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'add_new_messages.html'
    success_url = reverse_lazy('messages')

    def form_valid(self, form):
        # Автоматически присваиваем текущего пользователя как владельца
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_object(self, queryset=None):
        # Получаем объект по PK без фильтрации по владельцу.
        # Проверка владельца будет выполнена в OwnerRequiredMixin.
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk:
            return get_object_or_404(self.model, pk=pk)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = self.object is not None
        return context


class MessageDeleteView(OwnerRequiredMixin, CustomLoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'message_confirm_delete.html'
    success_url = reverse_lazy('messages')

    def get_object(self, queryset=None):
        # Получаем объект по PK без фильтрации по владельцу.
        # Проверка владельца будет выполнена в OwnerRequiredMixin.
        pk = self.kwargs.get(self.pk_url_kwarg)
        return get_object_or_404(self.model, pk=pk)


class MailingListView(CustomLoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user
        # Создаем уникальный ключ кеша для каждого пользователя (или для всех, если это менеджер)
        if user.is_staff:
            cache_key = 'all_mailings_list'
        else:
            cache_key = f'user_mailings_list_{user.pk}'

        mailings_queryset = cache.get(cache_key)

        if mailings_queryset is None:
            if user.is_staff:
                # Менеджеры видят все рассылки
                mailings_queryset = super().get_queryset()
            else:
                # Обычные пользователи - только свои
                mailings_queryset = super().get_queryset().filter(owner=user)

            # Кешируем результат на 5 минут (300 секунд)
            cache.set(cache_key, mailings_queryset, 300)
        return mailings_queryset


class MailingCreateUpdateView(OwnerRequiredMixin, CustomLoginRequiredMixin, CreateView, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'creating_mailing.html'
    success_url = reverse_lazy('mailings')

    def get_form_kwargs(self):
        # Передаем текущего пользователя в форму для фильтрации связанных объектов
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Автоматически присваиваем текущего пользователя как владельца
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_object(self, queryset=None):
        # Получаем объект по PK без фильтрации по владельцу.
        # Проверка владельца будет выполнена в OwnerRequiredMixin.
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk:
            return get_object_or_404(self.model, pk=pk)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = self.object is not None
        return context


class MailingDeleteView(OwnerRequiredMixin, CustomLoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings')

    def get_object(self, queryset=None):
        # Получаем объект по PK без фильтрации по владельцу.
        # Проверка владельца будет выполнена в OwnerRequiredMixin.
        pk = self.kwargs.get(self.pk_url_kwarg)
        return get_object_or_404(self.model, pk=pk)


class FilteredMailingListView(CustomLoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing_list.html'
    context_object_name = 'mailings'
    status_filter = None

    def get_queryset(self):
        # Менеджеры видят все рассылки по статусу, обычные пользователи - только свои по статусу
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)

        if self.status_filter:
            queryset = queryset.filter(status=self.status_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.status_filter == Mailing.STATUS_CREATED:
            context['page_title'] = 'Созданные рассылки'
        elif self.status_filter == Mailing.STATUS_RUNNING:
            context['page_title'] = 'Запущенные рассылки'
        elif self.status_filter == Mailing.STATUS_COMPLETED:
            context['page_title'] = 'Завершенные рассылки'
        else:
            context['page_title'] = 'Все рассылки'
        return context


class MailingAttemptListView(CustomLoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = 'mailing_attempts.html'
    context_object_name = 'attempts'
    paginate_by = 20  # Опционально, для больших списков

    def get_queryset(self):
        # Менеджеры видят все попытки рассылок, обычные пользователи - только свои
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(mailing__owner=self.request.user)


def feature_list_view(request):
    """
    Отображает список функций сайта, сгруппированных по категориям.
    """
    features = get_categorized_features()
    return render(request, 'feature_list.html', {'categorized_features': features})


@login_required
@require_POST
def toggle_mailing_status(request, pk):
    """
    Переключает статус рассылки между 'created' и 'running'.
    Менеджеры могут отключать любые рассылки при наличии соответствующих прав.
    """
    mailing = get_object_or_404(Mailing, pk=pk)

    # Если пользователь не является владельцем, проверяем наличие специфического права
    if mailing.owner != request.user and not request.user.has_perm('mailing_service.can_toggle_any_mailing_status'):
        messages.error(request, "У Вас недостаточно прав для выполнения этого действия.")
        return redirect('mailings')

    if mailing.status == Mailing.STATUS_CREATED:
        mailing.status = Mailing.STATUS_RUNNING
        messages.success(request, f"Рассылка '{mailing.message.subject}' успешно запущена.")
    elif mailing.status == Mailing.STATUS_RUNNING:
        mailing.status = Mailing.STATUS_CREATED
        messages.info(request, f"Рассылка '{mailing.message.subject}' успешно остановлена.")
    # Если статус 'completed', ничего не делаем

    mailing.save()
    return redirect('mailings')


@login_required
@require_POST
@login_required
@require_POST
def send_single_mailing(request, pk):
    """
    Отправляет письма для одной конкретной рассылки.
    Менеджеры могут отправлять любые рассылки при наличии соответствующих прав.
    """
    mailing = get_object_or_404(Mailing, pk=pk)

    # Если пользователь не является владельцем, проверяем наличие специфического права
    if mailing.owner != request.user and not request.user.has_perm('mailing_service.can_send_any_mailing'):
        messages.error(request, "У Вас недостаточно прав для выполнения этого действия.")
        return redirect('mailings')

    if not mailing.recipients.exists():
        messages.warning(request,
                         f'Рассылка "{mailing.message.subject}" (ID: {mailing.id}) не имеет получателей. '
                         f'Письма не отправлены.')
        return redirect('mailings')

    sent_count = 0
    failed_count = 0
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')

    for recipient in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=from_email,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            MailingAttempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                status=MailingAttempt.STATUS_SUCCESS,
                error_message=""
            )
            sent_count += 1
        except Exception as e:
            error_detail = str(e)
            MailingAttempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                status=MailingAttempt.STATUS_FAILED,
                error_message=error_detail
            )
            failed_count += 1
            user_friendly_message = f"Не удалось отправить письмо на {recipient.email}. "
            if "getaddrinfo failed" in error_detail:
                user_friendly_message += ("Проверьте настройки почтового сервера (EMAIL_HOST, EMAIL_PORT) "
                                          "или сетевое подключение.")
            else:
                user_friendly_message += f"Причина: {error_detail}"
            messages.error(request, user_friendly_message)

    messages.success(request,
                     f'Отправка рассылки "{mailing.message.subject}" (ID: {mailing.id}) завершена. '
                     f'Отправлено: {sent_count}, Ошибок: {failed_count}.')

    # Обновляем статус рассылки на "Завершена" после отправки
    if mailing.status != Mailing.STATUS_COMPLETED:
        mailing.status = Mailing.STATUS_COMPLETED
        mailing.save()
        messages.info(request, f'Статус рассылки "{mailing.message.subject}" обновлен на "Завершена".')

    return redirect('mailings')


def send_mailing_view(request):
    if not request.user.is_authenticated:
        messages.error(request,
                       "Вы не можете просматривать и управлять сообщениями, рассылками, получателями,"
                       " т.к. у вас нет прав. "
                       "Можете <a href='/users/login/'>войти</a> или <a href='/users/register/'>зарегистрироваться</a> "
                       "и переходить куда нужно.")
        return redirect('home')

    if request.method == 'POST':
        # Передаем текущего пользователя в форму для фильтрации рассылок
        form = MailingSendForm(request.POST, user=request.user)
        if form.is_valid():
            mailing = form.cleaned_data['mailing']

            # Проверка прав доступа для send_mailing_view
            # Менеджеры могут отправлять любые рассылки, обычные пользователи - только свои.
            if not request.user.is_staff and mailing.owner != request.user:
                messages.error(request, "У вас нет прав для отправки этой рассылки.")
                return redirect('send_mailing')

            if not mailing.recipients.exists():
                messages.warning(request,
                                 f'Рассылка "{mailing.message.subject}" (ID: {mailing.id}) '
                                 f'не имеет получателей. Письма не отправлены.')
                return redirect('send_mailing')

            sent_count = 0
            failed_count = 0
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')

            for recipient in mailing.recipients.all():
                try:
                    send_mail(
                        subject=mailing.message.subject,
                        message=mailing.message.body,
                        from_email=from_email,
                        recipient_list=[recipient.email],
                        fail_silently=False,
                    )
                    # Создаем запись об успешной попытке рассылки
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        recipient=recipient,
                        status=MailingAttempt.STATUS_SUCCESS,
                        error_message=""
                    )
                    sent_count += 1
                except Exception as e:
                    # Создаем запись о неуспешной попытке рассылки
                    error_detail = str(e)
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        recipient=recipient,
                        status=MailingAttempt.STATUS_FAILED,
                        error_message=error_detail
                    )
                    failed_count += 1
                    user_friendly_message = f"Не удалось отправить письмо на {recipient.email}. "

                    if "getaddrinfo failed" in error_detail:
                        user_friendly_message += ("Проверьте настройки почтового сервера (EMAIL_HOST, EMAIL_PORT)"
                                                  "или сетевое подключение.")
                    else:
                        user_friendly_message += f"Причина: {error_detail}"
                    messages.error(request, user_friendly_message)

            messages.success(request,
                             f'Отправка рассылки "{mailing.message.subject}" (ID: {mailing.id}) завершена.'
                             f'Отправлено: {sent_count}, Ошибок: {failed_count}.')
            return redirect('send_mailing')
    else:
        # Передаем текущего пользователя в форму для фильтрации рассылок
        form = MailingSendForm(user=request.user)
    return render(request, 'send_mailing.html', {'form': form})


def contacts_view(request):
    contact_info = {
        'country': 'Россия',
        'inn': '1234567890',
        'address': 'г. Москва, ул. Примерная, д. 1, офис 101',
    }
    form = ContactForm()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Здесь можно добавить логику отправки email или сохранения сообщения
            messages.success(request, 'Ваше сообщение успешно отправлено!')
            return redirect('contacts')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')

    return render(request, 'contacts.html', {'contact_info': contact_info, 'form': form})
