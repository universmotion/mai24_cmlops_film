FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

COPY ./app/api.py ./api.py

RUN apt-get update && apt-get install -y build-essential \
    pkg-config

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN rm requirements.txt
