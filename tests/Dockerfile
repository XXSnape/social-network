FROM python:3.10-slim

WORKDIR /app
COPY poetry.lock pyproject.toml ./

RUN python -m pip install --no-cache-dir poetry==1.8.3 \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY .env .env
COPY files files
COPY conftest.py conftest.py
COPY test_app.py test_app.py
COPY fixtures fixtures
CMD alembic upgrade head && pytest --cov=src .