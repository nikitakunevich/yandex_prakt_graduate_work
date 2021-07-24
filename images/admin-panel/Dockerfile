FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

#ARG UID=2000
#ARG GID=2000
#ARG USER=admin_panel
#ARG GROUP=application
ARG ROOT_APP=/app/

WORKDIR $ROOT_APP

#RUN groupadd -g $GID $GROUP && \
#    useradd -u $UID -g $GID -m $USER

RUN python -m pip install --upgrade pip && \
    pip install pipenv

COPY Pipfile Pipfile.lock $ROOT_APP

RUN pipenv install --system --ignore-pipfile

COPY entrypoint.sh $ROOT_APP
COPY mod_admin $ROOT_APP

#RUN chown -R $USER:$GROUP $ROOT_APP

#USER $USER
ENTRYPOINT ["bash", "entrypoint.sh"]
