FROM docker.io/python:latest


WORKDIR /app


RUN apt-get update


COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt