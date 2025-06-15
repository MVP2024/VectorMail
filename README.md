# 📨 VectorMail

VectorMail — это Django-приложение для управления электронными рассылками с возможностью ручной и программной отправки.

---

## 🚀 Возможности

- 🧑‍💼 **Управление клиентами**: Хранение email, ФИО и комментариев
- 📨 **Создание сообщений**: Редактирование темы и тела писем
- 📅 **Рассылки**: Настройка времени, статуса и получателей
- 🛠️ **Админка Django**: Полный CRUD для всех сущностей
- 🖥️ **Веб-интерфейс**: Ручная отправка рассылок через форму
- 📦 **Команды управления**:
    - `load_initial_data` — загрузка тестовых данных
    - `send_mailing` — отправка по ID

---

## 🧪 Технологии

- 🐍 Python 3.8+
- 🐘 PostgreSQL
- 🏗️ Django 5.2
- 📧 Email-бэкенды (console/SMTP)

---

## 🛠️ Установка

1. **Клонирование репозитория**
   ```
   git clone https://github.com/your-username/VectorMail.git
   cd VectorMail
   ```

2. **База данных**
   - Установите PostgreSQL
   - Создайте базу данных и пользователя согласно .env

3. **Виртуальное окружение**

    ```
        python -m venv .venv
        .venv\Scripts\activate  # Windows
        source .venv/bin/activate  # Linux/macOS
    ```
4. **Зависимости**

    ```
        pip install -r requirements.txt
    ```

5. **Переменные окружения**

    ```
       copy .env.example .env  # Windows
       # cp .env.example .env # Linux/macOS
    ```

6. **Миграции**

    ```
       python manage.py migrate
   
    ```

7**Суперпользователь**

    ```
        python manage.py createsuperuser
    ```

8***Тестовые данные***

    ```
        python -Xutf8 manage.py load_initial_data
    ```

9**Запуск**

    ```
        python manage.py runserver
    ```

## 🧪 Команды управления

- Отправка рассылки по ID:
    
    ``` 
        python manage.py send_mailing <mailing_id>
        
    ```

- Загрузка тестовых данных:
    ```
        python manage.py load_initial_data
    ```

## 🛠️ Установка Redis

### Установка
**Windows**:
1. Скачайте Redis с [официального репозитория](https://github.com/microsoftarchive/redis/releases)
2. Установите через установщик или запустите `redis-server.exe` напрямую

**Linux**:
    ```
        sudo apt update
        sudo apt install redis
    ```

### Запуск

**Windows:**
    ```
        redis-server.exe
    ```

**LINUX**

    ```
        sudo service redis start
        # Или
        redis-server
    ```

**Проверка**

    ```
       redis-cli ping
        # Ожидаемый ответ: PONG 
    ```

**Для мониторирования**

    ```
        redis-cli MONITOR
    ```

## ⚠️ Redis требуется для работы кеширования (настроен в settings.py через CACHES). 
## Убедитесь, что сервер запущен перед использованием приложения.

## ⚠️ Важно

- Для Windows используйте -Xutf8 при загрузке данных
- Убедитесь, что Redis запущен: redis-server
- Настройте EMAIL_BACKEND в .env для реальной отправки писем
- MEDIA_ROOT (media/) должен быть доступен для записи

## 🧑‍💼 Управление пользователями
- Расширенная модель пользователя с полями: отчество, дата рождения, телефон, аватар
- Ручная активация аккаунтов администратором
- Система восстановления пароля (сброс по email)
- Админ-панель с управлением статусом пользователей (актив/заблокирован)
- Валидация аватаров (форматы JPEG/PNG/GIF, ограничение 5МБ)

## 🔄 Дополнительные возможности
- Кеширование на Redis (время жизни 5 минут, сжатие zlib)
- Локализация на русский язык (LANGUAGE_CODE = "ru")
- Автоматическое обновление кеша (UpdateCacheMiddleware)
- Система уведомлений через messages framework

## 🛠️ Установка (дополнительно)
- **Миграции для users**: `python manage.py migrate users`
- **Email-конфигурация**: Настройте SMTP-параметры в `.env` для активации аккаунтов
- **Redis**: Убедитесь, что Redis-сервер запущен на `redis://127.0.0.1:6379/1`

## 📁 Структура проекта

VectorMail/
├── mailing_service/ # Приложение для управления рассылками
│ ├── models.py # Модели: Mailing, Message, Recipient
│ ├── views.py # Логика управления рассылками
│ ├── templates/ # Шаблоны для рассылок и управления
│ └── fixtures/ # Тестовые данные (initial_data.json)
├── users/ # Приложение пользователей
│ ├── models.py # Расширенная модель User
│ ├── forms.py # Формы регистрации/профиля
│ └── templates/ # Шаблоны аутентификации и профиля
├── static/ # Статические файлы (CSS, JS)
├── media/ # Загрузка аватаров и других файлов
└── VectorMail/ # Основной проект
├── settings.py # Настройки Redis, email, кеширования
└── urls.py # Маршруты приложений

## 📧 Email-функционал

- Активация аккаунта: Отправка ссылки на email с токеном
- Сброс пароля: Шаблоны и логика для password_reset
- Рассылки: Настройка SMTP в .env для реальной отправки

🛠️ Установка (полная)

## 📌 Примечания

- Для Windows используйте -Xutf8 при загрузке данных
- В .env настройте EMAIL_BACKEND для тестирования или реальной отправки
- Данные фикстур находятся в mailing_service/fixtures/initial_data.json
- Для работы с Redis установите и запустите сервер Redis
- В `.env` обязательно настройте параметры EMAIL_* для функций активации и сброса пароля
- При работе с аватарами убедитесь, что MEDIA_ROOT доступен для записи

## 📦 Лицензия

 MIT License — см. README.md