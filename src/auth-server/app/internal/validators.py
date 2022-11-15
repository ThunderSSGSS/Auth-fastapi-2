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


#___________AUTH_VALIDATORS_______________________________________#

class ToEncodeValidator(BaseDictValidator):
	sub:UUID
	user_id:UUID
	permissions:List[str]
	groups:List[str]
	exp:datetime
	token_type:str

	@classmethod
	def is_access_token(cls, data:dict):
		if data['token_type']=='access': return True
		return False
	
	@classmethod
	def is_refresh_token(cls, data:dict):
		if data['token_type']=='refresh': return True
		return False

class DecodedValidator(ToEncodeValidator):
	exp:int


#_______________MANAGERS_VALIDATORS_________________________________#
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
	salt:Optional[str]
	is_complete:Optional[bool]

	#validators
	_validator1 = validator('email', allow_reuse=True)(validate_email)
	_validator2 = validator('username', allow_reuse=True)(validate_username)

class CreateUserValidator(UpdateUserValidator, BaseManagerCreateValidator):
	id:UUID
	email:str
	username:str
	password:str
	salt:str


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


#______________SERVICES_VALIDATORS__________________________________#

class SignupValidator(BaseDictValidator):
	email:str
	username:str
	password:str

	#validators
	_validator1 = validator('email', allow_reuse=True)(validate_email)
	_validator2 = validator('username', allow_reuse=True)(validate_username)
	_validator3 = validator('password', allow_reuse=True)(validate_password)

class CompleteSignupValidator(BaseDictValidator):
	email:str
	random:str
	password:str

	#validators
	_validator1 = validator('email', allow_reuse=True)(validate_email)
	_validator2 = validator('password', allow_reuse=True)(validate_password)

class AuthenticationValidator(BaseDictValidator):
	email:str
	password:str

	#validators
	_validator1 = validator('email', allow_reuse=True)(validate_email)
	_validator2 = validator('password', allow_reuse=True)(validate_password)

class RegenerateSignupRandomValidator(BaseDictValidator):
	email:str

	#validators
	_validator1 = validator('email', allow_reuse=True)(validate_email)

class RegeneratePasswordRandomValidator(RegenerateSignupRandomValidator):
	pass

class ForgetPasswordValidator(RegenerateSignupRandomValidator):
	pass

class RestaurePasswordValidator(BaseDictValidator):
	email:str
	random:str
	new_password:str

	#validators
	_validator1 = validator('email', allow_reuse=True)(validate_email)
	_validator2 = validator('new_password', allow_reuse=True)(validate_password)

class SetPasswordValidator(BaseDictValidator):
	password:str
	new_password:str
	
	#validators
	_validator1 = validator('password', 'new_password', allow_reuse=True)(validate_password)

class SetEmailValidator(BaseDictValidator):
	password:str
	new_email:str
	
	#validators
	_validator1 = validator('new_email', allow_reuse=True)(validate_email)
	_validator2 = validator('password', allow_reuse=True)(validate_password)

class CompleteSetEmailValidator(BaseDictValidator):
	random:str

class SetUsernameValidator(BaseDictValidator):
	password:str
	new_username:str

	#validators
	_validator1 = validator('new_username', allow_reuse=True)(validate_username)
	_validator2 = validator('password', allow_reuse=True)(validate_password)


#______________INTRA_SERVICES_VALIDATORS_____________________________________#

class CheckAuthorizationValidator(BaseDictValidator):
	permissions:Optional[List[str]]
	groups:Optional[List[str]]
	access_token:str


#_____________ADMIN_CRUD_SERVICES_VALIDATORS__________________________________#

#_____USER____#

class CreateUserAdminValidator(BaseDictValidator):
	email:str
	username:str
	password:str
	is_complete:bool

	#validators
	_validator1 = validator('email', allow_reuse=True)(validate_email)
	_validator2 = validator('username', allow_reuse=True)(validate_username)
	_validator3 = validator('password', allow_reuse=True)(validate_password)

class SetUserAdminValidator(BaseDictValidator):
	id:UUID
	username:Optional[str]
	is_complete:Optional[bool]

	#validators
	_validator1 = validator('username', allow_reuse=True)(validate_username)

class GetUserAdminValidator(BaseDictValidator):
	id:UUID


#_____PERMISSION____#

class CreatePermissionAdminValidator(BaseDictValidator):
	id:str

	#validators
	_validator1 = validator('id', allow_reuse=True)(validate_name)

class GetPermissionAdminValidator(CreatePermissionAdminValidator):
	pass


#_____GROUP________#

class CreateGroupAdminValidator(CreatePermissionAdminValidator):
	pass

class GetGroupAdminValidator(CreateGroupAdminValidator):
	pass


#_____________OTHERS_ADMIN_SERVICES_VALIDATORS__________________________________#

#____PERMISSION_GRANT____#

class GrantPermissionToUserValidator(BaseDictValidator):
	user_id:UUID
	permission_id:str

	#validators
	_validator1 = validator('permission_id', allow_reuse=True)(validate_name)

class GrantPermissionToGroupValidator(BaseDictValidator):
	group_id:str
	permission_id:str
	
	#validators
	_validator1 = validator('permission_id', 'group_id', allow_reuse=True)(validate_name)

class RemoveUserPermissionValidator(GrantPermissionToUserValidator):
	pass

class RemoveGroupPermissionValidator(GrantPermissionToGroupValidator):
	pass


#_______GROUP_GRANT_______#

class AddUserToGroupValidator(BaseDictValidator):
	user_id:UUID
	group_id:str
	
	#validators
	_validator1 = validator('group_id', allow_reuse=True)(validate_name)

class RemoveUserFromGroupValidator(AddUserToGroupValidator):
	pass


#________SESSION_MANAGEMENT_______#

class RemoveSessionValidator(BaseDictValidator):
	user_id:UUID
	session_id:Optional[UUID]