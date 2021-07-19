# Kårspexets IT-system

[![Build Status](https://circleci.com/gh/Karspexet/Karspexet.svg?style=svg)](https://circleci.com/gh/Karspexet/Karspexet)
[![Codacy](https://api.codacy.com/project/badge/Grade/8834660783b148a1af9d76807d4a1008)](https://www.codacy.com/app/Frost/Karspexet?utm_source=github.com&utm_medium=referral&utm_content=Karspexet/Karspexet&utm_campaign=Badge_Grade)
[![Test Coverage](https://api.codacy.com/project/badge/Coverage/8834660783b148a1af9d76807d4a1008)](https://www.codacy.com/app/Frost/Karspexet?utm_source=github.com&utm_medium=referral&utm_content=Karspexet/Karspexet&utm_campaign=Badge_Coverage)

Detta repo innehåller Kårspexets IT-system, vilket just nu är dess
biljettsystem.

## Setup

Skapa en `env.json`-fil med följande för att få stripe-integrationen att fungera:

```json
{
  "stripe": {
    "secret_key": "sk_test_...",
    "publishable_key": "pk_test_..."
  }
}
```

För att installera alla appens beroenden körs kommandot:

```sh
pip install -U poetry
poetry install
```

För datalagring används en Postgres server som förväntas finnas på port `5432`.
Därefter går servern att starta genom kommandot:

```sh
python3 manage.py runserver
```

Rikta sedan din favoritwebläsare mot `localhost:8000` för att se hemsidan.

## Tester

Kör `postgresql` via docker i en terminal:

```sh
docker run -it --rm -p 5432:5432 circleci/postgres:9.6.2
```

Kör sedan testerna mot den i en annan terminal:

```sh
DATABASE_URL=postgres://root@127.0.0.1:5432/circle_test pytest
```

## Linters

För att försöka hålla javascript-koden hyfsat homogen använder vi `eslint`.

Den kan man köra på sina javascript-filer genom:

    eslint var/nu/min/fil/ligger.js

Det kan hända att den klagar på en massa saker, och att vissa av de sakerna går
att fixa automatiskt. Då kan man göra det med:

    eslint --fix var/nu/min/fil/ligger.js
