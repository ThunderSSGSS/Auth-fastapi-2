from celery import Celery, Task
from app.internal.settings import RABBITMQ_URI, RABBITMQ_QUEUES

broker_auth=RABBITMQ_URI

class EmailTask(Task):
	queue=RABBITMQ_QUEUES['EMAILS']

class DatabaseTask(Task):
	queue=RABBITMQ_QUEUES['DB_TRANSACTIONS']


celery_auth = Celery('auth_server', broker=broker_auth)


#______________________________Email_Tasks___________________________#
@celery_auth.task(base=EmailTask, name='send_email')
def send_email(to, subject, message):
	return _send_email(to, subject, message)

@celery_auth.task(base=EmailTask, name='send_signup_email')
def send_signup_email(to, random_code, data_dict):
	return _send_signup_email(to, random_code)

@celery_auth.task(base=EmailTask, name='send_password_forget_email')
def send_password_forget_email(to, random_code, data_dict):
	return _send_password_forget_email(to, random_code)

@celery_auth.task(base=EmailTask, name='send_set_email')
def send_set_email(to, random_code, data_dict):
	return _send_set_email(to, random_code)


#____________________________DATABASE_TASKS____________________________#
@celery_auth.task(base=DatabaseTask, name='process_transactions')
def process_transactions(transactions_list):
	return _process_transactions(transactions_list)