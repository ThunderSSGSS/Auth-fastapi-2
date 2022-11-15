import os
from .validators import (DatabaseUriValidator, ExpValidator, RabbitmqUriValidator, 
	RabbitmqQueueValidator)


def _not_setted_exception(env_name:str):
	return ValueError('The ENV '+env_name+' not setted')

def _invalid_exception(env_name:str):
	return ValueError('The ENV '+env_name+' value is invalid')



#____________TEST_MODE_____________________#

TEST_MODE = None
if os.environ.get('TEST_MODE', 'NO')=='YES': TEST_MODE = True
else: TEST_MODE = False


#______________DATABASE_SETTINGS____________#

#<username>:<password>@<hostname>/<db_name>
DATABASE_URI = os.environ.get('DATABASE_URI')

#__ENV_TEST____#
if not TEST_MODE:
	if DATABASE_URI is None: raise _not_setted_exception('DATABASE_URI')
	elif not DatabaseUriValidator.is_valid(DATABASE_URI): raise _invalid_exception('DATABASE_URI')


#_______________CACHE_SETTINGS________________#

CACHE={
	#redis://<hostname>
	'CACHE_URI': os.environ.get('CACHE_URI'),
	'PREFIX':'auth'
}


#________________AUTH_SETTINGS________________#

AUTH={
	#Can be RS256 or HS256
	#IF HS256, set only private_key else, set private_key and public_key 
	'JWT_ALGORITHM': os.environ.get('JWT_ALGORITHM', 'HS256'),
	'PRIVATE_KEY': os.environ.get('PRIVATE_KEY'),
	'PUBLIC_KEY':  os.environ.get('PUBLIC_KEY', os.environ.get('PRIVATE_KEY')),

	'SECRET_KEY': os.environ.get('SECRET_KEY'),

	'ACCESS_TOKEN_EXP': os.environ.get('ACCESS_TOKEN_EXP', '20'),
	'REFRESH_TOKEN_EXP': os.environ.get('REFRESH_TOKEN_EXP', '50')
}

#__ENV_TEST____#
if AUTH['SECRET_KEY'] is None: raise _not_setted_exception('SECRET_KEY')
elif len(AUTH['SECRET_KEY'])!=32: raise _invalid_exception('SECRET_KEY')

if AUTH['PRIVATE_KEY'] is None: raise _not_setted_exception('PRIVATE_KEY')
if AUTH['JWT_ALGORITHM'] == 'RS256' and AUTH['PUBLIC_KEY']==AUTH['PRIVATE_KEY']: raise _not_setted_exception('PUBLIC_KEY')

if not ExpValidator.is_valid(AUTH['ACCESS_TOKEN_EXP']): raise _invalid_exception('ACCESS_TOKEN_EXP')
if not ExpValidator.is_valid(AUTH['REFRESH_TOKEN_EXP']): raise _invalid_exception('REFRESH_TOKEN_EXP')


#_____RANDOM_SETTINGS___________________________#

RANDOM_EXP = os.environ.get('RANDOM_EXP','10')

#__ENV_TEST____#
if not ExpValidator.is_valid(RANDOM_EXP): raise _invalid_exception('RANDOM_EXP')
RANDOM_EXP = int(RANDOM_EXP)


#____________RABBITMQ_SETTINGS__________________#

#amqp://<username>:<password>@<hostname>/<vhost_name>
RABBITMQ_URI = os.environ.get('RABBITMQ_URI')

RABBITMQ_QUEUES={
	'EMAILS': os.environ.get('EMAILS_QUEUE','auth_emails'),
	'DB_TRANSACTIONS': os.environ.get('DB_TRANSACTIONS_QUEUE','auth_db_transactions')
}

#__ENV_TEST____#
if not TEST_MODE:
	if RABBITMQ_URI is None: raise _not_setted_exception('RABBITMQ_URI')
	elif not RabbitmqUriValidator.is_valid(RABBITMQ_URI): raise _invalid_exception('RABBITMQ_URI')

	if not RabbitmqQueueValidator.is_valid(RABBITMQ_QUEUES['EMAILS']): raise _invalid_exception('EMAILS_QUEUE')
	if not RabbitmqQueueValidator.is_valid(RABBITMQ_QUEUES['DB_TRANSACTIONS']): raise _invalid_exception('DB_TRANSACTIONS_QUEUE')