FROM python:3.9-slim

ENV PYTHONPATH=/app/src

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./src/. ./
EXPOSE 8888

CMD uvicorn --port 8888 --host 0.0.0.0 main:app
