# Базовый образ
FROM python:3.11-slim

# Установка зависимостей
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Устанавливаем переменные окружения
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Запускаем приложение
CMD ["flask", "run"]