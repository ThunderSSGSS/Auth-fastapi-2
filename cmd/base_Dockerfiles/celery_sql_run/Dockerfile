FROM python:3.7-alpine

WORKDIR /code

COPY requirements.txt .

RUN apk add --no-cache libpq && apk add --no-cache --virtual .build-deps gcc build-base libffi-dev musl-dev postgresql-dev \
&& pip3 install --no-cache-dir --upgrade -r requirements.txt \
&& apk del .build-deps gcc libffi-dev musl-dev postgresql-dev build-base