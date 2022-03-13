# Kårspexets IT-system

Detta repo innehåller koden för https://kårspexet.se/.

## Installation

För att installera alla appens beroenden kör du dessa kommandon i en
terminal:

```sh
pip install -U poetry
poetry install
npm install
```

Starta sedan databasen i bakgrunden med `docker`, och initialisera dess
tabeller:

```sh
docker-compose up -d postgres

poetry run manage.py migrate
```

## Användning

Sätt sedan igång byggandet av CSS- & JS-filer i en terminal med:

```sh
npm start
```

Och starta servern i en annan terminal med:

```sh
poetry run python manage.py runserver
```

Nu kan du gå till http://localhost:8000 för att se hemsidan.

## Tester

Se till att databasen är igång som beskrivet ovan, och kör sedan testerna
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
