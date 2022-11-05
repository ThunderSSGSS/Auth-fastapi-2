FROM celery_sql_run:v1

COPY app /code/app
CMD ["celery","-A","app.celery", "worker","--loglevel=INFO"]