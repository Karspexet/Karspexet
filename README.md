# Kårspexets IT-system

[![Build Status](https://semaphoreci.com/api/v1/projects/77599d4a-92c6-4a85-b54f-3774f78321b0/678193/badge.svg)](https://semaphoreci.com/frost/karspexet)
[![Code Climate](https://codeclimate.com/github/Karspexet/Karspexet/badges/gpa.svg)](https://codeclimate.com/github/Karspexet/Karspexet)
[![Test Coverage](https://codeclimate.com/github/Karspexet/Karspexet/badges/coverage.svg)](https://codeclimate.com/github/Karspexet/Karspexet/coverage)

Detta repo innehåller Kårspexets IT-system, vilket just nu är dess
biljettsystem.

# Setup

Skapa en `env.json`-fil med följande för att få stripe-integrationen att fungera:

```json
{
  "stripe": {
    "secret_key": "sk_test_...",
    "publishable_key": "pk_test_..."
  }
}
```
