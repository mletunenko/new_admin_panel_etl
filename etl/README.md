
Сервис django админки
Сервис синхронизации индекса elasticsearch с БД postgres movies_database

Пояснения по docker compose
- Порты остаются открытыми, поскольку данный docker compose предназначен для разработки, а не для продакшен среды
- postgres запускается на 30000 порту
- для nginx прокинут 81 порт 

## Запуск приложения

### Docker-compose

1. Выполнить команды:
```bash
dc up [--build] -d
```
### Локальный запуск

1. Активировать venv и создать .env по образцу
2. Установить зависимости
```bash
pip install --upgrade pip && pip install -r requirements.txt
```
3. Используйте docker-compose.yml 
Так же поднятие контейнеров с сервисами для локальной работы доступны через 

```bash
 dc up [--build] -d admin_elasticsearch admin_postgres admin_django-migrations admin_postgres_to_es
```

4. Запуск приложения из директории etl

```bash
python manage.py runserver 9000
```

## Связанные репозитории

Сервис выдачи контента
- https://github.com/mletunenko/Async_API_sprint_1_team

Сервис административной панели 
- https://github.com/mletunenko/new_admin_panel_sprint_3

Сервис авторизации
- https://github.com/mletunenko/Auth_sprint_1

