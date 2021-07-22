FROM python:3.9-slim

ARG APP_ROOT=/app/

WORKDIR $APP_ROOT
COPY Pipfile Pipfile.lock $APP_ROOT

RUN python -m pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --system --ignore-pipfile

COPY src $APP_ROOT
COPY entrypoint.sh $APP_ROOT

EXPOSE 8000
ENTRYPOINT ["bash", "entrypoint.sh"]