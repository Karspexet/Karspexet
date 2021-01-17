FROM python:3.6-alpine3.11 as builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/virtualenv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /app
RUN python -m venv $VIRTUAL_ENV
RUN addgroup -g 1000 app && adduser -D -h /app -G app -u 1000 app

RUN apk add --upgrade --no-cache \
  # Needed to pip install and run psycopg2-binary \
  postgresql-dev \
  # Needed to run PIL \
  jpeg


FROM builder as deps
RUN apk add --upgrade --no-cache \
  # Needed to pip install pillow \
  gcc jpeg-dev musl-dev zlib-dev \
  # Needed to pip install uwsgi \
  linux-headers

COPY Pipfile Pipfile.lock ./
RUN pip install --upgrade pip wheel pipenv \
  && pipenv install \
  && rm -r /root/.cache


FROM builder as runner
COPY --chown=app --from=deps $VIRTUAL_ENV $VIRTUAL_ENV
COPY --chown=app . /app
ARG RELEASE=""
RUN echo "$RELEASE" > RELEASE.txt
RUN python manage.py assets build \
  && python manage.py collectstatic --noinput \
  && chown -R app:app /app

CMD ["uwsgi", "--ini", "/app/karspexet/uwsgi.ini"]
