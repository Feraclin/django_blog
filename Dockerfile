FROM python:3.10
RUN apt update && apt -y install gettext-base

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ['python3', 'manage.py', 'migrate']
CMD ['python3', 'manage.py', 'loaddata', './db/db.json']
CMD ['python3', 'manage.py', 'runserver', '0.0.0.0:8000']
