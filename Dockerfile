FROM python:3.9-slim as builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/virtualenv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /app
RUN python -m venv $VIRTUAL_ENV \
 && useradd --uid 1000 app \
 && chown app /app

FROM builder as deps

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel poetry

COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev --no-interaction --no-root


FROM builder as runner
USER app:app
EXPOSE 8000
CMD ["gunicorn", "karspexet.wsgi", "--bind", "0.0.0.0:8000"]

COPY --chown=app:app --from=deps $VIRTUAL_ENV $VIRTUAL_ENV
COPY --chown=app:app . /app
RUN python manage.py assets build \
  && python manage.py collectstatic --noinput
