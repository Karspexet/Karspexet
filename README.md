# Kårspexets IT-system

[![Build Status](https://circleci.com/gh/Karspexet/Karspexet.svg?style=svg)](https://circleci.com/gh/Karspexet/Karspexet)
[![Codacy](https://api.codacy.com/project/badge/Grade/8834660783b148a1af9d76807d4a1008)](https://www.codacy.com/app/Frost/Karspexet?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Karspexet/Karspexet&amp;utm_campaign=Badge_Grade)
[![Test Coverage](https://api.codacy.com/project/badge/Coverage/8834660783b148a1af9d76807d4a1008)](https://www.codacy.com/app/Frost/Karspexet?utm_source=github.com&utm_medium=referral&utm_content=Karspexet/Karspexet&utm_campaign=Badge_Coverage)

Detta repo innehåller Kårspexets IT-system, vilket just nu är dess
biljettsystem.

## Docker setup

1. Ladda ner och installera Docker
2. Gå till mappen för ditt klonade repo och skriv `docker build` för att bygga image:en, skriv sedan `docker-compose up` för att starta docker containers.
3. Kör `docker exec -it karspexet_djangocms_1 bash ./create_superuser.sh ` för att skapa ett admin konto.

Vi skulle kunna länka in källkoden som en `VOLUME` till docker bilden
men detta skapar inte lika säker produktionssättning.

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
pip install -r requirements/dev.txt
```
För datalagring används en Postgres server som förväntas finnas på port `5432`.
Därefter går servern att starta genom kommandot:
```sh
python3 manage.py runserver
```
Rikta sedan din favoritwebläsare mot `localhost:8000` för att se hemsidan.

## Linters

För att försöka hålla javascript-koden hyfsat homogen använder vi `eslint`.

Den kan man köra på sina javascript-filer genom:

    eslint var/nu/min/fil/ligger.js

Det kan hända att den klagar på en massa saker, och att vissa av de sakerna går
att fixa automatiskt. Då kan man göra det med:

    eslint --fix var/nu/min/fil/ligger.js
