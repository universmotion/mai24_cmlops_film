FROM python:3.10-slim

WORKDIR /app

RUN rm -rf ./app/test

COPY ./requirements.txt ./requirements.txt

COPY ./app/ ./

RUN apt-get update && apt-get install -y build-essential \
    pkg-config

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN mkdir -p /app/data/models

RUN rm requirements.txt
