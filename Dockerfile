FROM python:3.9-slim as builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/virtualenv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /app
RUN python -m venv $VIRTUAL_ENV \
 && useradd --uid 1000 app \
 && chown app /app
# Install postfix to get django_sendmail_backend working
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
    postfix=3.5.6-1+b1 \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

FROM builder as deps-py

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel poetry

COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev --no-interaction --no-root


FROM node:16.2.0 AS deps-js
WORKDIR /app
COPY package-lock.json package.json /app/
RUN npm ci --no-optional && npm cache clean --force

COPY assets/ /app/assets/
COPY karspexet/templates/ /app/karspexet/templates/
COPY tailwind.config.js .postcssrc /app/
RUN npm run build


FROM builder as runner
USER app:app
EXPOSE 8000
CMD ["gunicorn", "karspexet.wsgi", "--bind", "0.0.0.0:8000"]

COPY --chown=app:app --from=deps-py $VIRTUAL_ENV $VIRTUAL_ENV
COPY --chown=app:app --from=deps-js /app/dist /app/dist
COPY --chown=app:app . /app
ARG DEBUG=false
RUN python manage.py collectstatic --noinput
