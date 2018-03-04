FROM python:3

WORKDIR /usr/src/app

COPY requirements/dev.txt ./
COPY requirements/base.txt ./
RUN pip install --no-cache-dir -r dev.txt

COPY . .
