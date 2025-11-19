FROM docker.io/python:latest

WORKDIR /app


RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*


COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=backend.settings