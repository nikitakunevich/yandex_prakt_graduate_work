#!/bin/bash

python3 manage.py migrate
#python3 manage.py collectstatic --no-input
if [ ! -z ${ADMIN_USER} ] && [ ! -z ${ADMIN_PASS} ]
then
  echo "Creating admin user with provided credentials"
  echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('${ADMIN_USER}', '', '${ADMIN_PASS}')" | python manage.py shell
fi

gunicorn mod_admin.wsgi -b 0.0.0.0:8000
