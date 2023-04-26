FROM python:3.10.4

WORKDIR /app

COPY . .

RUN pip install pipenv

RUN pipenv install
