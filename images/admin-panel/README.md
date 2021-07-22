Чтобы запустить проект в docker-compose:

```./run.sh start```

При запуске:
* будут подняты postgresql, nginx, gunicorn с django приложением.
* созданы вольюмы для базы, статики.
* ETL достанет данные из sqlite и положит в postgresql.
* будут применены django-миграции к данным, чтобы они соответствовали моделям.
* Статические файлы будут сохранены в volume для отдачи nginx-ом.
* Будет создан админ с логин: admin, паролем: admin.

nginx будет доступен на порту **8080**.

Чтобы удалить все контейнеры и volumes:

```./run.sh stop```

Чтобы запустить проект без docker, а на django dev-server, можно после запуска скрипта ./run.sh start выполнить команду:
```
set -a;source ../deploys/local.env; set +a; ./manage.py runserver
```
(В такой конфигурации работает debug-toolbar).

Сервер подключится к postgresql базе в docker.
