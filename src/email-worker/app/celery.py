from celery import Celery
from .settings import RABBITMQ_URI, DEFAULT_QUEUE


broker=RABBITMQ_URI

app = Celery('email_worker', broker=broker, include=['app.tasks'])
app.conf.task_default_queue= DEFAULT_QUEUE