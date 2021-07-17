FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG UID=2000
ARG GID=2000
ARG USER=flask
ARG GROUP=application
ARG ROOT_APP=/app

RUN groupadd -g $GID $GROUP && \
    useradd -u $UID -g $GID -m $USER && \
    mkdir $ROOT_APP

COPY Pipfile Pipfile.lock $ROOT_APP/

WORKDIR $ROOT_APP

RUN python -m pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --system --ignore-pipfile

COPY src/ $ROOT_APP/
ENV FLASK_APP   main.py

RUN chown -R $USER:$GROUP $ROOT_APP

USER $USER

CMD ["python", "main.py"]