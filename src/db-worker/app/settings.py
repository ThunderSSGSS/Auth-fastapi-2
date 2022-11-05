import os
from .validators import (DatabaseUriValidator, RabbitmqUriValidator, 
	RabbitmqQueueValidator, EmailValidator)


def _not_setted_exception(env_name:str):
	return ValueError('The ENV '+env_name+' not setted')

def _invalid_exception(env_name:str):
	return ValueError('The ENV '+env_name+' value is invalid')


#_____________RABBITMQ_SETTINGS_______________#

#amqp://<username>:<password>@<hostname>/<vhost_name>
RABBITMQ_URI = os.environ.get('RABBITMQ_URI')
DEFAULT_QUEUE = os.environ.get('WORKER_DEFAULT_QUEUE','auth_db_transactions')

#__ENV_TEST____#
if RABBITMQ_URI is None: raise _not_setted_exception('RABBITMQ_URI')
elif not RabbitmqUriValidator.is_valid(RABBITMQ_URI): raise _invalid_exception('RABBITMQ_URI')
if not RabbitmqQueueValidator.is_valid(DEFAULT_QUEUE): raise _invalid_exception('WORKER_DEFAULT_QUEUE')


#______________AUTH_SETTINGS_________________#
ADMIN_USER_EMAIL = os.environ.get('ADMIN_USER_EMAIL')

#__ENV_TEST____#
if ADMIN_USER_EMAIL is not None:
	if not EmailValidator.is_valid(ADMIN_USER_EMAIL): raise _invalid_exception('ADMIN_USER_EMAIL')  



#______________CACHE_SETTINGS________________#

BACKEND={
	#redis://<hostname>
	'CACHE_URI': os.environ.get('CACHE_URI'),
	'PREFIX':'auth'
}


#_______________DATABASE_SETTINGS______________#

#<username>:<password>@<hostname>/<db_name>
DATABASE_URI = os.environ.get('DATABASE_URI')

#__ENV_TEST____#
if DATABASE_URI is None: raise _not_setted_exception('DATABASE_URI')
elif not DatabaseUriValidator.is_valid(DATABASE_URI): raise _invalid_exception('DATABASE_URI')