FROM python:3.6 AS builder
ENV VIRTUAL_ENV=/virtualenv
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"
WORKDIR /app

RUN python -m venv ${VIRTUAL_ENV}

COPY Pipfile Pipfile.lock ./
RUN pip install --upgrade pip wheel pipenv && pipenv install


COPY . /app
ARG RELEASE=""
RUN echo "$RELEASE" > RELEASE.txt
RUN python manage.py assets build
RUN python manage.py collectstatic --noinput


RUN addgroup --gid=1000 app && useradd --home=/app --gid=app app && chown -R app /app
CMD ["uwsgi", "--ini", "/app/karspexet/uwsgi.ini"]
