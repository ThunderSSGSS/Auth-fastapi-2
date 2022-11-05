import re
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, validator, ValidationError


#___________________STR VALIDATORS________________________________#
class BaseStrValidator():
	regex=None #must be regex str

	@classmethod
	def validate(cls, data:str):
		if not re.fullmatch(cls.regex, data): raise ValueError('invalid')
	
	@classmethod
	def is_valid(cls, data:str):
		if re.fullmatch(cls.regex, data): return True
		return False

class EmailValidator(BaseStrValidator):
    regex=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

class PasswordValidator(BaseStrValidator):
    regex=r'[A-Za-z0-9@#$%^&+=]{8,20}'

class UsernameValidator(BaseStrValidator):
    regex=r'[A-Za-z0-9@#$%^&+=_]{5,20}'

class NameValidator(BaseStrValidator):
    regex=r'[A-Za-z0-9_]{3,30}'


#_________SETTINGS_VALIDATORS_________#

class DatabaseUriValidator(BaseStrValidator):
	#<username>:<password>@<hostname>/<db_name>
	regex=r'^[A-Za-z0-9_-]{3,}[:][A-Za-z0-9#=_-]{3,}[@][A-Za-z0-9_-]{2,}[/][A-Za-z0-9_-]{1,}$'

class ExpValidator(BaseStrValidator):
	regex=r'^[0-9]{1,}$'

class RabbitmqUriValidator(BaseStrValidator):
	#amqp://<username>:<password>@<hostname>/<vhost_name>
	regex=r'^[a][m][q][p][:][/]{2}[A-Za-z0-9_-]{3,}[:][A-Za-z0-9#=_-]{3,}[@][A-Za-z0-9_-]{2,}[/][A-Za-z0-9_/-]{1,}$'

class RabbitmqQueueValidator(BaseStrValidator):
	regex=r'^[A-Za-z0-9_-]{3,}$'


#_________________________DICT_VALIDATORS__________________________________#
class BaseDictValidator(BaseModel):
	@classmethod
	def validate(cls, data:dict):
		p = cls.parse_obj(data)
	
	@classmethod
	def is_valid(cls, data:dict):
		try: p = cls.parse_obj(data)
		except ValidationError as ex: return False
		return True

def _validate(validator_class, value, msg:str):
	if not validator_class.is_valid(value): raise ValueError(msg)
	return value

def validate_email(value:str):
	return _validate(EmailValidator, value, 'invalid email')

def validate_password(value:str):
	return _validate(PasswordValidator, value, 'invalid password')

def validate_username(value:str):
	return _validate(UsernameValidator, value, 'invalid username')

def validate_name(value:str):
	return _validate(NameValidator, value, 'invalid name')