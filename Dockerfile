# Вказуємо базовий образ
FROM python:3.12-slim-bullseye

# Налаштування змінних оточення
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Встановлюємо робочу директорію
WORKDIR /app

# Оновлюємо пакетний менеджер і встановлюємо gcc
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо файл з залежностями
COPY requirements.txt /app/

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо всі файли проекту в контейнер
COPY . /app/

# Виконуємо команду для збирання статичних файлів (для Django проектів)
RUN python manage.py collectstatic --noinput

# Відкриваємо порт 8000 для з'єднань
EXPOSE 8000

# Вказуємо команду запуску додатку
ENTRYPOINT [ "gunicorn", "coolsite.wsgi", "-b", "0.0.0.0:8000"]
