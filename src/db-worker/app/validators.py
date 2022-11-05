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


#_______________CRUD_VALIDATORS_________________________________#
class BaseManagerUpdateValidator(BaseDictValidator):
	updated:datetime

class BaseManagerCreateValidator(BaseManagerUpdateValidator):
	created:datetime


#_____LOG_______#

class CreateLogValidator(BaseManagerCreateValidator):
	id:UUID
	user_id:Optional[UUID]
	object_type:str
	object_id:str
	action:str
	message:Optional[str]
	
	#validators
	_validator1 = validator('object_type', allow_reuse=True)(validate_name)

#_____USER______#

class UpdateUserValidator(BaseManagerUpdateValidator):
	email:Optional[str]
	username:Optional[str]
	password:Optional[str]
	is_complete:Optional[bool]

	#validators
	_validator1 = validator('email', allow_reuse=True)(validate_email)
	_validator2 = validator('username', allow_reuse=True)(validate_username)

class CreateUserValidator(UpdateUserValidator, BaseManagerCreateValidator):
	id:UUID
	email:str
	username:str
	password:str


#_____RANDOM______#

class UpdateRandomValidator(BaseManagerUpdateValidator):
	key:str

class CreateRandomValidator(UpdateRandomValidator, BaseManagerCreateValidator):
	id:UUID
	flow:str
	value:Optional[str]


#_____PERMISSION____#

class UpdatePermissionValidator(BaseManagerUpdateValidator):
	id:str

	#validators
	_validator1 = validator('id', allow_reuse=True)(validate_name)

class CreatePermissionValidator(UpdatePermissionValidator, BaseManagerCreateValidator):
	is_original:bool


#_____GROUP________#

class CreateGroupValidator(CreatePermissionValidator):
	pass

class UpdateGroupValidator(UpdatePermissionValidator):
	pass


#______SESSION__________#

class CreateSessionValidator(BaseManagerCreateValidator):
	session_id:UUID
	user_id:UUID
	expirated:datetime


#____USER_PERMISSION____#

class CreateUserPermissionValidator(BaseManagerCreateValidator):
	user_id:UUID
	permission_id:str

	#validators
	_validator1 = validator('permission_id', allow_reuse=True)(validate_name)

#____USER_GROUP_____#

class CreateUserGroupValidator(BaseManagerCreateValidator):
	user_id:UUID
	group_id:str
	
	#validators
	_validator1 = validator('group_id', allow_reuse=True)(validate_name)

#_____GROUP_PERMISSION____#

class CreateGroupPermissionValidator(BaseManagerCreateValidator):
	group_id:str
	permission_id:str
	is_original:bool

	#validators
	_validator1 = validator('group_id', 'permission_id', allow_reuse=True)(validate_name)