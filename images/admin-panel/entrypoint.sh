#!/bin/bash

echo "migrate"
python3 manage.py migrate
echo "collectstatic"
python3 manage.py collectstatic -v 0 --no-input

if [ ! -z ${ADMIN_USER} ] && [ ! -z ${ADMIN_PASS} ]
then
  echo "Creating admin user with provided credentials"
  echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('${ADMIN_USER}', '', '${ADMIN_PASS}')" | python manage.py shell
fi

gunicorn -b 0.0.0.0:8000 config.wsgi --log-level ${LOG_LEVEL}