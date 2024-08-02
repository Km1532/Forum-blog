# Використовуйте базовий образ, який підтримує потрібну версію Python
FROM python:3.12-slim-bullseye

# Оновлюємо pip, setuptools і wheel до останніх версій
RUN pip install --upgrade pip setuptools wheel

# Перевірка версії Python
RUN python --version

# Налаштовуємо змінні середовища
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Встановлюємо робочу директорію
WORKDIR /app

# Встановлюємо залежності для компіляції (gcc і build-essential)
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо файл з залежностями
COPY requirements.txt /app/

# Встановлюємо Python-залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо всі файли проекту в контейнер
COPY . /app/

# Збираємо статичні файли (зазвичай це робиться в процесі розгортання)
RUN python manage.py collectstatic --noinput

# Відкриваємо порт для доступу
EXPOSE 8000

# Вказуємо команду для запуску сервера
ENTRYPOINT ["gunicorn", "coolsite.wsgi:application", "-b", "0.0.0.0:8000"]
