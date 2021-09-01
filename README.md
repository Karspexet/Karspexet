# Kårspexets IT-system

Detta repo innehåller koden för https://kårspexet.se/.

## Setup

För att installera alla appens beroenden körs kommandot:

```sh
pip install -U poetry
poetry install
```

Starta den databas som behövs i bakgrunden med `docker`, och kör sedan
databasmigreringar för att sätta upp den.

```sh
docker-compose up -d postgres

poetry run python manage.py migrate
```

Sätt sedan igång byggandet av CSS- & JS-filer i en terminal med:

```sh
npm run watch
```

Och starta servern i en annan terminal med:

```sh
poetry run python manage.py runserver
```

Nu kan du gå till http://localhost:8000 för att se hemsidan.

## Tester

Se till att databasen är igång som i steget ovan, och kör sedan testerna
med:

```sh
pytest
```

## Linters

Vi har en bunt olika linters och kodformatterare som går att köra med
verktyget https://pre-commit.com/. Du kör det på filerna med:

```sh
pre-commit run -a
```
