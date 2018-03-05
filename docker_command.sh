#!/bin/bash
set -e

until pg_isready -h $DATABASE_HOST -p $DATABASE_PORT; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - Migrating database"
python3 manage.py migrate

>&2 echo "Starting Server!"
python3 manage.py runserver 0.0.0.0:$PORT
