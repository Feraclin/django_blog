#### Проект Блог с лентой постов

##### Технологии

    DRF, Celery, Redis, POSTGRESQL

## Запуск


##### 1) Создать настройки окружения и указать окружение в settings.py

##### 2) Собрать контейнеры

    docker-compose build

##### 2) Запустить контейнер

    docker-compose up
    
##### 3) Перейти по адресу

    http://0.0.0.0:8080/swagger/


### Тестирование

    coverage run --omit=*/venv/*,*/migrations/*,*/django_blog/django_blog/*,*test*  manage.py test blog

### Тестовая база данных в каталоге db дамп и sql

