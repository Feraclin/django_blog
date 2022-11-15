Восстановление всей базы данных

экспорт

python manage.py dumpdata --exclude auth.permission --exclude contenttypes > ./db/db.json

импорт

python manage.py loaddata ./db/db.json
