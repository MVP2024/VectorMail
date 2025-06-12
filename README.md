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

2. **Виртуальное окружение**

    ```
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    source .venv/bin/activate  # Linux/macOS
    ```
3. **Зависимости**

    ```
    pip install -r requirements.txt
    ```

4. **Переменные окружения**
    ```
   copy .env.example .env  # Windows
   # cp .env.example .env # Linux/macOS

   ```
5. **Миграции**

    ```python manage.py migrate```

6. **Суперпользователь**

    ```python manage.py createsuperuser```

7. ***Тестовые данные***

    ```python -Xutf8 manage.py load_initial_data```

8. **Запуск**

    ```python manage.py runserver```

## 📁 Структура проекта

    ```
    VectorMail/
    ├── mailing_service/          # Основное приложение
    │   ├── models.py             # Модели: Client, Message, Mailing
    │   ├── admin.py              # Регистрация в админке
    │   ├── forms.py              # Формы для веб-интерфейса
    │   └── management/commands/  # Пользовательские команды
    ├── VectorMail/               # Настройки проекта
    ├── templates/                # HTML-шаблоны
    ├── static/                   # Статические файлы
    ├── media/                    # Медиафайлы
    ├── .env                      # Конфиденциальные настройки
    └── README.md                 # Документация
    
    ```

## 📌 Примечания

- Для Windows используйте -Xutf8 при загрузке данных
- В .env настройте EMAIL_BACKEND для тестирования или реальной отправки
- Данные фикстур находятся в mailing_service/fixtures/initial_data.json

## 📦 Лицензия

 MIT License — см. README.md