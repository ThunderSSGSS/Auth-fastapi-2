FROM celery_run:v1

RUN adduser -S myuser
USER myuser
WORKDIR /home/myuser

COPY app /home/myuser/app

CMD ["celery","-A","app.celery", "worker","--loglevel=INFO"]