# yamdb_final
yamdb_final

## Описание
Api_yamdb - проект, в котором пользователи могут делиться своими отзывами о произведениях при помощи API.

### Основные используемые технологии
1. Python 3.7 
2. Django 3.2
3. Django REST framework 
4. PostgreSQL 
5. Docker
6. GIT (https://github.com/git-guides)

### Документация и возможности API:
Для просмотра документиации к проекту подключен redoc. Для просмотра используйте http://localhost/redoc/

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/Deron-The-Great/infra_sp2.git
```
```
cd infra
```

Развернуть контейнеры:
```
docker-compose up -d --build
```

Cоздать файл .env в дирректории /infra со следующим содержанием:
```
SECRET_KEY=default-key
DB_ENGINE=django.db.backends.postgresql 
DB_NAME=postgres # имя БД
POSTGRES_USER=postgres # логин для подключения к БД
POSTGRES_PASSWORD= # пароль для подключения к БД
DB_HOST=db # название сервиса
DB_PORT=5432 # порт для подключения к БД
```

Осуществить миграции, создать суперпользователя и собрать статику:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```


Наполнить БД:
```
docker-compose exec web python manage.py loaddata ../infra/fixtures.json 
```

![workflow status](https://github.com/Deron-The-Great/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

### Автор проекта:
- [Шубин Сергей](https://github.com/Deron-The-Great/)
