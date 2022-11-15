FROM python:3.10
RUN apt update && apt -y install gettext-base

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
