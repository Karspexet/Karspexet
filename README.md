# Kårspexets IT-system

[![Build Status](https://semaphoreci.com/api/v1/frost/karspexet/branches/master/shields_badge.svg)](https://semaphoreci.com/frost/karspexet)
[![Code Climate](https://codeclimate.com/github/Karspexet/Karspexet/badges/gpa.svg)](https://codeclimate.com/github/Karspexet/Karspexet)
[![Test Coverage](https://codeclimate.com/github/Karspexet/Karspexet/badges/coverage.svg)](https://codeclimate.com/github/Karspexet/Karspexet/coverage)

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

## Linters

För att försöka hålla javascript-koden hyfsat homogen använder vi `eslint`.

Den kan man köra på sina javascript-filer genom:

    eslint var/nu/min/fil/ligger.js

Det kan hända att den klagar på en massa saker, och att vissa av de sakerna går
att fixa automatiskt. Då kan man göra det med:

    eslint --fix var/nu/min/fil/ligger.js
