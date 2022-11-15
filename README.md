Восстановление всей базы данных

экспорт

python manage.py dumpdata --exclude auth.permission --exclude contenttypes > db.json

импорт

python manage.py loaddata db.json
