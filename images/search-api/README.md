 additional_claims={'prm': user.is_premium, 'roles': user_roles},

roles: admin, child, adult

# Проектная работа 5 спринта

Для запуска всех тестов:
```shell
./run.sh tests
```

Для запуска тестов во время разработки тестов можно сперва запустить elastic,redis,api:
```shell
./run.sh tests_setup
```
А затем перезапускать только тесты:
```shell
./run.sh tests_run
```