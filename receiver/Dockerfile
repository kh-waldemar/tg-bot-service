FROM python:3.9.0-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /receiver && apt-get update
WORKDIR /receiver

COPY ./receiver/pyproject.toml /receiver/
COPY ./receiver/poetry.lock /receiver/
RUN pip install poetry && poetry config virtualenvs.create false && \
    poetry install --no-root && \
    pip install --no-cache-dir -U telethon && \
    pip install flask

COPY ./receiver /receiver
