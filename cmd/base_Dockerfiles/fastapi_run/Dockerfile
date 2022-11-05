FROM python:3.8-alpine

WORKDIR /code

COPY requirements.txt .
RUN apk add --no-cache libpq && apk add --no-cache --virtual .build-deps build-base libffi-dev musl-dev postgresql-dev \
&& pip3 install --no-cache-dir --upgrade -r requirements.txt \
&& apk del .build-deps build-base libffi-dev musl-dev postgresql-dev

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]