FROM python:3.9-slim

WORKDIR /app/
COPY Pipfile Pipfile.lock /app/
RUN python -m pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --system --ignore-pipfile

COPY src postgres_to_es/

CMD python -m postgres_to_es.daemon --postgres-url ${PG_URL} --elastic-url ${ES_URL} --redis-host ${REDIS_HOST}