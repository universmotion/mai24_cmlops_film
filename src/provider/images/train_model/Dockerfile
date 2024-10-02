FROM python:3.10-slim

RUN apt-get update -y && apt-get install -y libpq-dev gcc

WORKDIR /app

COPY ./main.py ./main.py
COPY ./datamodel.py ./datamodel.py
COPY ./utils.py ./utils.py
COPY ./requirements.txt ./requirements.txt

RUN mkdir -p /app/data/models

RUN pip install -r requirements.txt