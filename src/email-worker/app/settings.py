import os
from .validators import RabbitmqUriValidator, RabbitmqQueueValidator, EmailValidator


def _not_setted_exception(env_name:str):
	return ValueError('The ENV '+env_name+' not setted')

def _invalid_exception(env_name:str):
	return ValueError('The ENV '+env_name+' value is invalid')


#_____________RABBITMQ_SETTINGS_______________#

#amqp://<username>:<password>@<hostname>/<vhost_name>
RABBITMQ_URI = os.environ.get('RABBITMQ_URI')
DEFAULT_QUEUE = os.environ.get('WORKER_DEFAULT_QUEUE','auth_emails')

#__ENV_TEST____#
if RABBITMQ_URI is None: raise _not_setted_exception('RABBITMQ_URI')
elif not RabbitmqUriValidator.is_valid(RABBITMQ_URI): raise _invalid_exception('RABBITMQ_URI')
if not RabbitmqQueueValidator.is_valid(DEFAULT_QUEUE): raise _invalid_exception('WORKER_DEFAULT_QUEUE')


#______________BACKEND_SETTINGS________________#

BACKEND={
	#redis://<hostname>:<port>
	'CACHE_URI': os.environ.get('CACHE_URI'),
	'PREFIX':'auth'
}

#_______________EMAIL_SETTINGS______________#

EMAIL={
	'email':os.environ.get('SENDER_EMAIL'),
	'password':os.environ.get('SENDER_EMAIL_PASSWORD')
}

#__ENV_TEST____#
if EMAIL['email'] is None: raise _not_setted_exception('SENDER_EMAIL')
elif not EmailValidator.is_valid(EMAIL['email']): raise _invalid_exception('SENDER_EMAIL')
if EMAIL['password'] is None: raise _not_setted_exception('SENDER_EMAIL_PASSWORD')