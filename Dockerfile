# Використовуємо офіційний образ Python
FROM python:3.12

# Встановлюємо poetry
RUN pip install poetry

# Встановлюємо робочу директорію у контейнері
WORKDIR /app

# Встановлення gettext
RUN apt-get update && apt-get install -y gettext

# Копіюємо файли poetry.lock і pyproject.toml до /app
COPY poetry.lock pyproject.toml /app/

# Встановлюємо залежності, не створюючи віртуального середовища
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Копіюємо інші файли проекту
COPY . /app


# Надання прав на виконання для скрипта
RUN chmod +x /app/ops/scripts/start-server.sh

# Вказуємо команду для виконання скрипта
CMD ["bash", "/app/ops/scripts/start-server.sh"]
