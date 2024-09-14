FROM python:3.10-slim

RUN apt-get update -y && apt-get install -y libpq-dev gcc

WORKDIR /app

COPY ./main.py ./main.py
COPY ./build_features.py ./build_features.py
COPY ./requirements.txt ./requirements.txt

RUN mkdir -p /app/data/to_ingest

RUN pip install -r requirements.txt