# Используем официальный образ Python (выберите нужную версию)
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Скопируем файл зависимостей (предположим, у вас есть requirements.txt)
COPY requirements.txt ./

# Установим зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем весь проект в контейнер
COPY . .

# По умолчанию команда запускает бота
CMD ["python", "main.py"]
