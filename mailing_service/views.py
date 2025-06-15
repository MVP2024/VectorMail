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
                           "Для просмотра и управления сообщениями, рассылками и получателями необходимо войти в систему или зарегистрироваться. Пожалуйста, <a href='/users/login/'>войдите</a> или <a href='/users/register/'>зарегистрируйтесь</a>.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

@cache_page(60 * 1)  # Кешировать страницу на 1 минуту (60 секунд)
@vary_on_cookie      # Кешировать отдельно для каждого пользователя (по кукам сессии)
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


class RecipientFormView(CustomLoginRequiredMixin, CreateView, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'add_new_recipient.html'
    success_url = reverse_lazy('clients')

    def form_valid(self, form):
        # Автоматически присваиваем текущего пользователя как владельца
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_object(self, queryset=None):
        # Пользователь может редактировать только своих получателей.
        # Менеджер не может редактировать чужие данные через эту форму.
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk:
            # Если пользователь - менеджер, он может просматривать чужие данные,
            # но для редактирования/удаления ему доступны только его собственные.
            # Поэтому здесь фильтруем по owner=self.request.user
            if self.request.user.is_staff:
                # Менеджер может просматривать, но не редактировать чужие данные через эту форму.
                # Чтобы менеджер мог редактировать только свои, оставляем фильтр.
                # Если бы менеджер мог редактировать чужие, фильтр бы убрали.
                return get_object_or_404(self.model, pk=pk, owner=self.request.user)
            return get_object_or_404(self.model, pk=pk, owner=self.request.user)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = self.object is not None
        return context


class RecipientDeleteView(CustomLoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = 'recipient_confirm_delete.html'
    success_url = reverse_lazy('clients')

    def get_queryset(self):
        # Пользователь может удалять только своих получателей.
        # Менеджер не может удалять чужие данные.
        return super().get_queryset().filter(owner=self.request.user)


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


class MessageDetailView(CustomLoginRequiredMixin, DetailView):
    model = Message
    template_name = 'message_detail.html'
    context_object_name = 'message'

    def get_queryset(self):
        # Менеджеры видят все сообщения, обычные пользователи - только свои
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(owner=self.request.user)


class MessageCreateUpdateView(CustomLoginRequiredMixin, CreateView, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'add_new_messages.html'
    success_url = reverse_lazy('messages')

    def form_valid(self, form):
        # Автоматически присваиваем текущего пользователя как владельца
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_object(self, queryset=None):
        # Пользователь может редактировать только свои сообщения.
        # Менеджер не может редактировать чужие данные через эту форму.
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk:
            if self.request.user.is_staff:
                return get_object_or_404(self.model, pk=pk, owner=self.request.user)
            return get_object_or_404(self.model, pk=pk, owner=self.request.user)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = self.object is not None
        return context


class MessageDeleteView(CustomLoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'message_confirm_delete.html'
    success_url = reverse_lazy('messages')

    def get_queryset(self):
        # Пользователь может удалять только свои сообщения.
        # Менеджер не может удалять чужие данные.
        return super().get_queryset().filter(owner=self.request.user)


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


class MailingCreateUpdateView(CustomLoginRequiredMixin, CreateView, UpdateView):
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
        # Пользователь может редактировать только свои рассылки.
        # Менеджер не может редактировать чужие данные через эту форму.
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk:
            if self.request.user.is_staff:
                return get_object_or_404(self.model, pk=pk, owner=self.request.user)
            return get_object_or_404(self.model, pk=pk, owner=self.request.user)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = self.object is not None
        return context


class MailingDeleteView(CustomLoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings')

    def get_queryset(self):
        # Пользователь может удалять только свои рассылки.
        # Менеджер не может удалять чужие данные.
        return super().get_queryset().filter(owner=self.request.user)


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
    Менеджеры могут отключать любые рассылки. Пользователи - только свои.
    """
    if request.user.is_staff:
        mailing = get_object_or_404(Mailing, pk=pk)
    else:
        mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

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
def send_single_mailing(request, pk):
    """
    Отправляет письма для одной конкретной рассылки.
    Менеджеры могут отправлять любые рассылки. Пользователи - только свои.
    """
    if request.user.is_staff:
        mailing = get_object_or_404(Mailing, pk=pk)
    else:
        mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

    if not mailing.recipients.exists():
        messages.warning(request,
                         f'Рассылка "{mailing.message.subject}" (ID: {mailing.id}) не имеет получателей. Письма не отправлены.')
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
                user_friendly_message += "Проверьте настройки почтового сервера (EMAIL_HOST, EMAIL_PORT) или сетевое подключение."
            else:
                user_friendly_message += f"Причина: {error_detail}"
            messages.error(request, user_friendly_message)

    messages.success(request,
                     f'Отправка рассылки "{mailing.message.subject}" (ID: {mailing.id}) завершена. Отправлено: {sent_count}, Ошибок: {failed_count}.')

    # Обновляем статус рассылки на "Завершена" после отправки
    if mailing.status != Mailing.STATUS_COMPLETED:
        mailing.status = Mailing.STATUS_COMPLETED
        mailing.save()
        messages.info(request, f'Статус рассылки "{mailing.message.subject}" обновлен на "Завершена".')

    return redirect('mailings')


def send_mailing_view(request):
    if not request.user.is_authenticated:
        messages.error(request,
                       "Вы не можете просматривать и управлять сообщениями, рассылками, получателями, т.к. у вас нет прав. Можете <a href='/users/login/'>войти</a> или <a href='/users/register/'>зарегистрироваться</a> и переходить куда нужно.")
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
                                 f'Рассылка "{mailing.message.subject}" (ID: {mailing.id}) не имеет получателей. Письма не отправлены.')
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
                        user_friendly_message += "Проверьте настройки почтового сервера (EMAIL_HOST, EMAIL_PORT) или сетевое подключение."
                    else:
                        user_friendly_message += f"Причина: {error_detail}"
                    messages.error(request, user_friendly_message)

            messages.success(request,
                             f'Рассылка "{mailing.message.subject}" (ID: {mailing.id}) завершена. Отправлено: {sent_count}, Ошибок: {failed_count}.')
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
