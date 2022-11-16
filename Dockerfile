FROM python:3.10
RUN apt update && apt -y install gettext-base
RUN python -m pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt


# добавить .dockerignore
COPY . .
