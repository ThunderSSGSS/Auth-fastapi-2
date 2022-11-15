import abc
import uuid
import asyncio
import json
from datetime import datetime

#interfaces
from app.internal.domain.interfaces import ManagerInterface, RandomManagerInterface, RelationalManagerInterface
from .interfaces import AuthServiceInterface, NoAuthServiceInterface
from app.internal.adapter.interfaces import (TransactionProcessorInterface, EmailSenderInterface, 
	TokenGeneratorInterface, PasswordHasherInterface)

#others
from app.internal.exceptions import HTTPExceptionGenerator, DictValidatorException
from app.internal.validators import (BaseDictValidator, SignupValidator, AuthenticationValidator, RegenerateSignupRandomValidator, 
	RegeneratePasswordRandomValidator, ForgetPasswordValidator, RestaurePasswordValidator, CompleteSignupValidator, 
	SetPasswordValidator, SetEmailValidator, CompleteSetEmailValidator, SetUsernameValidator)
from app.internal import warnings as war





class BaseService():
	validator_class: None

	#_________________Operations_________________#

	def _validate_received_data(self, data: dict):

		try: self.validator_class.validate(data)
		except Exception as ex:
			raise HTTPExceptionGenerator(status_code=400, detail=json.loads(ex.json()))

	def _check_not_found(self, object, name:str):
		"""
		check if the object not exist and raise exception
		when the object is None it's mean that, the object not exist
		"""
		if object is None:
			raise HTTPExceptionGenerator(status_code=404,
				detail=HTTPExceptionGenerator.generate_detail(fields=[name], 
					error_type='not_found', msg=war.not_found_msg(name)))
		return object

	def _check_found(self, object, name:str):
		"""
		check if the object exist and raise exception
		when the object is not None it's mean that, the object exist
		"""
		if object is not None:
			raise HTTPExceptionGenerator(status_code=400,
				detail=HTTPExceptionGenerator.generate_detail(fields=[name], 
					error_type='exist', msg=war.exist_msg(name)))
	
	def _check_complete_signup(self, user_is_complete:bool, want_value:bool):

		if user_is_complete!= want_value:
			raise HTTPExceptionGenerator(status_code=400,
				detail=HTTPExceptionGenerator.generate_detail(fields=['signup'], 
					error_type='state', msg=war.complete_signup_msg(not want_value)))
	
	def _check_random_expiration(self, updated:datetime, want_value:bool, random_manager:RandomManagerInterface):

		error_type = 'expired'
		if want_value: error_type = 'not_expired'

		if want_value != random_manager.is_expired(updated):
			raise HTTPExceptionGenerator(status_code=400,
				detail=HTTPExceptionGenerator.generate_detail(fields=['random'], 
					error_type=error_type, msg=war.expired_msg('random',not want_value)))
	
	def _generate_password_salt(self): # on admin service i have this function too
		return uuid.uuid4()

#_________________________________NO_AUTH_SERVICES___________________________________________________#

class BaseAuthService(BaseService):

	def _auth_user(self, user, plain_password:str, is_complete:bool, 
		password_hasher: PasswordHasherInterface):

		#compare user passwords
		if not password_hasher.compare_passwords(plain_password+user.salt, user.password):
			raise HTTPExceptionGenerator(status_code=400,
				detail=HTTPExceptionGenerator.generate_detail(fields=['password'], 
					error_type='incorrect', msg=war.incorrect_password_msg()))

		#check complete signup
		self._check_complete_signup(user.is_complete, is_complete)


	def _validate_random(self, random, random_key:str, 
		random_manager:RandomManagerInterface):

		#check random expiration
		self._check_random_expiration(random.updated, False, random_manager)

		#compare random keys
		if random_key != random.key:
			raise HTTPExceptionGenerator(status_code=400,
				detail=HTTPExceptionGenerator.generate_detail(fields=['random'], 
					error_type='incorrect', msg=war.incorrect_msg('random')))


	async def _get_user_permissions_and_groups(self, user_id,
		user_permission_manager: RelationalManagerInterface,
		user_group_manager: RelationalManagerInterface,
		group_permission_manager: RelationalManagerInterface):

		#result[0] => user_permissions | result[1] => user_groups
		result = await asyncio.gather(*[
			user_permission_manager.get_many_by({'user_id':user_id}),
			user_group_manager.get_many_by({'user_id':user_id})])
		
		permission_names = []
		group_names = []

		for user_permission in result[0]:
			permission_names.append(user_permission.permission_id)

		courotine2 = []
		for user_group in result[1]:
			group_names.append(user_group.group_id)
			courotine2.append(group_permission_manager.get_many_by({'group_id':user_group.group_id}))

		if len(group_names)==0: return permission_names, group_names

		#result2 => group_permissions
		result2 = await asyncio.gather(*courotine2)
		for group_permissions in result2:
			for group_permission in group_permissions:
				permission_names.append(group_permission.permission_id)

		return permission_names, group_names


	async def _get_user_infos(self, user_id, username:str,
		user_permission_manager: RelationalManagerInterface,
		user_group_manager: RelationalManagerInterface,
		group_permission_manager: RelationalManagerInterface):
		
		permissions, groups = await self._get_user_permissions_and_groups(user_id, 
			user_permission_manager, user_group_manager, group_permission_manager)
		
		user_infos = {'user_id': str(user_id), 
			'permissions': permissions, 'groups': groups}

		return user_infos



#____________________SIGNUP_SERVICE____________________________#

class SignupService(BaseService, NoAuthServiceInterface):
	validator_class = SignupValidator

	def __init__(self, transaction_processor: TransactionProcessorInterface, 
		user_manager: ManagerInterface, user_group_manager: RelationalManagerInterface,
		random_manager: RandomManagerInterface, email_sender: EmailSenderInterface):

		self._transaction_processor = transaction_processor
		self._user_manager = user_manager
		self._user_group_manager = user_group_manager
		self._random_manager = random_manager
		self._email_sender = email_sender

	async def start_service(self, data: dict):
		
		#data.keys() = ['email', 'password', 'username']
		data['email'] = data['email'].lower()
		self._validate_received_data(data)

		#checks if the email exist
		self._check_found(await self._user_manager.get({'email':data['email']}), 'email')

		transactions_list = []

		#generating salt
		data['salt'] = str(self._generate_password_salt())
		data['password'] = data['password'] + data['salt']

		#create the user
		user, tran = self._user_manager.create(data)
		transactions_list.extend(tran)

		#create random
		random, tran = self._random_manager.create({'id':user.id, 'flow':'signup'})
		transactions_list.extend(tran)

		#add user to normal group
		user_group, tran = self._user_group_manager.create({'user_id':user.id, 'group_id':'normal'})
		transactions_list.extend(tran)

		#send signup email
		self._email_sender.send_signup_email(data['email'], random.key)
		
		#process transactions
		await self._transaction_processor.process(transactions_list)

		return {'id':user.id, 'email':data['email']}



#__________________COMPLETE_SIGNUP_SERVICE_____________________________#

class CompleteSignupService(BaseAuthService, NoAuthServiceInterface):
	validator_class = CompleteSignupValidator

	def __init__(self, transaction_processor: TransactionProcessorInterface,
		user_manager: ManagerInterface, random_manager: RandomManagerInterface,
		user_permission_manager: RelationalManagerInterface, user_group_manager: RelationalManagerInterface, 
		group_permission_manager: RelationalManagerInterface, session_manager: RelationalManagerInterface,
		token_generator: TokenGeneratorInterface, password_hasher: PasswordHasherInterface):

		self._transaction_processor= transaction_processor
		self._user_manager = user_manager
		self._random_manager = random_manager
		self._user_permission_manager = user_permission_manager
		self._user_group_manager = user_group_manager
		self._group_permission_manager = group_permission_manager
		self._session_manager = session_manager
		self._token_generator = token_generator
		self._password_hasher = password_hasher

	async def start_service(self, data: dict):

		#data.keys() = ['email', 'password', 'random']
		data['email'] = data['email'].lower()
		self._validate_received_data(data)

		#get the user by email
		user = self._check_not_found(
			await self._user_manager.get({'email':data['email']}),'email')

		#get random
		random = self._check_not_found(
			await self._random_manager.get({'id':user.id, 'flow':'signup'}),'random')
		
		transactions_list = []

		#check random validation and compare the keys
		self._validate_random(random, data['random'], self._random_manager)

		#compare passwords and check complete signup
		self._auth_user(user, data['password'], False, self._password_hasher)

		#set is_complete to true
		tran=self._user_manager.update({'id':user.id}, {'is_complete':True})
		transactions_list.extend(tran)

		#delete random
		tran=self._random_manager.delete({'id':user.id, 'flow':'signup'})
		transactions_list.extend(tran)

		#create session
		session, tran = self._session_manager.create({'user_id':user.id, 
			'expirated':self._token_generator.get_next_expirated()})
		transactions_list.extend(tran)

		#get user infos (permissions and groups)
		user_infos = await self._get_user_infos(user.id, user.username,
			self._user_permission_manager, self._user_group_manager, self._group_permission_manager)
		user_infos['sub'] = str(session.session_id)

		#process transactions
		await self._transaction_processor.process(transactions_list)

		#generate tokens
		return self._token_generator.create_tokens(user_infos)



#__________________REGENERATE_SIGNUP_RANDOM_SERVICE_____________________________#

class RegenerateSignupRandomService(BaseService, NoAuthServiceInterface):
	validator_class= RegenerateSignupRandomValidator

	def __init__(self, transaction_processor: TransactionProcessorInterface,
		user_manager: ManagerInterface, random_manager: RandomManagerInterface,
		email_sender: EmailSenderInterface):

		self._transaction_processor = transaction_processor
		self._user_manager = user_manager
		self._random_manager = random_manager
		self._email_sender = email_sender

	async def start_service(self, data: dict):
		
		#data.keys() = ['email']
		data['email'] = data['email'].lower()
		self._validate_received_data(data)

		#get the user by email
		user = self._check_not_found(
			await self._user_manager.get({'email':data['email']}),'email')
		
		#check signup state
		self._check_complete_signup(user.is_complete, False)
		
		#get random
		random = self._check_not_found(
			await self._random_manager.get({'id':user.id, 'flow':'signup'}),'random')
		
		#check random expiration
		self._check_random_expiration(random.updated, True, self._random_manager)
		
		transactions_list = []

		#regenerate random
		random_key = self._random_manager.generate_random()
		tran=self._random_manager.update({'id':random.id, 'flow':random.flow}, {'key':random_key})
		transactions_list.extend(tran)

		#send signup email
		self._email_sender.send_signup_email(user.email, random_key)

		#process transactions
		await self._transaction_processor.process(transactions_list)

		return {'detail':'random regenerated'}



#__________________AUTHENTICATION_SERVICE_____________________________#

class AuthenticationService(BaseAuthService, NoAuthServiceInterface):
	validator_class= AuthenticationValidator

	def __init__(self, transaction_processor: TransactionProcessorInterface,
		user_manager: ManagerInterface, user_permission_manager: RelationalManagerInterface,
		user_group_manager: RelationalManagerInterface, group_permission_manager: RelationalManagerInterface,
		session_manager: RelationalManagerInterface, token_generator: TokenGeneratorInterface, 
		password_hasher: PasswordHasherInterface):

		self._transaction_processor = transaction_processor
		self._user_manager = user_manager
		self._user_permission_manager = user_permission_manager
		self._user_group_manager = user_group_manager
		self._group_permission_manager = group_permission_manager
		self._session_manager = session_manager
		self._token_generator = token_generator
		self._password_hasher = password_hasher


	async def start_service(self, data: dict):
		
		#data.keys() = ['email', 'password']
		data['email'] = data['email'].lower()
		self._validate_received_data(data)

		#get the user by email
		user = self._check_not_found(
			await self._user_manager.get({'email':data['email']}),'email')
		
		#compare passwords and check complete signup
		self._auth_user(user, data['password'], True, self._password_hasher)
		
		transactions_list = []

		#create session
		session, tran = self._session_manager.create({'user_id':user.id, 
			'expirated':self._token_generator.get_next_expirated()})
		transactions_list.extend(tran)
		
		#get user infos (permissions and groups)
		user_infos = await self._get_user_infos(user.id, user.username,
			self._user_permission_manager, self._user_group_manager, self._group_permission_manager)
		user_infos['sub'] = str(session.session_id)
		
		#process transactions
		await self._transaction_processor.process(transactions_list)

		#generate tokens
		return self._token_generator.create_tokens(user_infos)



#__________________REFRESH_TOKEN_SERVICE_____________________________#

class RefreshTokenService(BaseService, NoAuthServiceInterface):

	def __init__(self, transaction_processor: TransactionProcessorInterface,
		session_manager: RelationalManagerInterface, token_generator: TokenGeneratorInterface):
		
		self._transaction_processor = transaction_processor
		self._session_manager = session_manager
		self._token_generator = token_generator

	async def start_service(self, data: dict):
		#decode refresh token
		decoded_refresh_token = self._token_generator.decode_refresh_token(data['refresh_token'])
		#check the session
		session = self._check_not_found(
			await self._session_manager.get({'session_id':decoded_refresh_token['sub'],
				'user_id':decoded_refresh_token['user_id']}), 'session')
		#create acess token
		return self._token_generator.create_access_token(decoded_refresh_token)



#__________________FORGET_PASSWORD_SERVICE_____________________________#

class ForgetPasswordService(BaseService, NoAuthServiceInterface):
	validator_class= ForgetPasswordValidator

	def __init__(self, transaction_processor: TransactionProcessorInterface,
		user_manager: ManagerInterface, random_manager: RandomManagerInterface,
		email_sender: EmailSenderInterface):

		self._transaction_processor = transaction_processor
		self._user_manager = user_manager
		self._random_manager = random_manager
		self._email_sender = email_sender

	async def start_service(self, data: dict):
		
		#data.keys() = ['email']
		data['email'] = data['email'].lower()
		self._validate_received_data(data)

		#get the user by email
		user = self._check_not_found(
			await self._user_manager.get({'email':data['email']}),'email')
		
		#check signup
		self._check_complete_signup(user.is_complete, True)

		#checks if the random exist
		self._check_found(await self._random_manager.get(
			{'id':user.id, 'flow':'password'}), 'random')
		
		transactions_list = []

		#create random
		random, tran = self._random_manager.create({'id':user.id, 'flow':'password'})
		transactions_list.extend(tran)
		
		#send forget passsword email
		self._email_sender.send_password_forget_email(user.email, random.key)

		#process transactions
		await self._transaction_processor.process(transactions_list)

		return {'detail':'forget password email sended'}



#__________________RESTAURE_PASSWORD_SERVICE_____________________________#

class RestaurePasswordService(BaseAuthService, NoAuthServiceInterface):
	validator_class= RestaurePasswordValidator

	def __init__(self, transaction_processor: TransactionProcessorInterface,
		user_manager: ManagerInterface, random_manager: RandomManagerInterface):

		self._transaction_processor = transaction_processor
		self._user_manager = user_manager
		self._random_manager = random_manager


	async def start_service(self, data: dict):
		
		#data.keys() = ['email', 'random', 'new_password']
		data['email'] = data['email'].lower()
		self._validate_received_data(data)

		#get the user by email
		user = self._check_not_found(
			await self._user_manager.get({'email':data['email']}),'email')
		
		#check signup
		self._check_complete_signup(user.is_complete, True)

		#get random
		random = self._check_not_found(await self._random_manager.get(
			{'id':user.id, 'flow':'password'}),'random')
		
		#check random expiration and compare the keys
		self._validate_random(random, data['random'], self._random_manager)

		transactions_list = []

		#generating salt
		salt_password = str(self._generate_password_salt())

		#set user password
		tran = self._user_manager.update({'id':user.id}, {'password': data['new_password']+salt_password, 'salt':salt_password})
		transactions_list.extend(tran)

		#delete random
		tran = self._random_manager.delete({'id':random.id, 'flow':random.flow})
		transactions_list.extend(tran)

		#process transactions
		await self._transaction_processor.process(transactions_list)

		return {'detail':'password restaured'}



#__________________REGENERATE_PASSWORD_RANDOM_SERVICE_____________________________#

class RegeneratePasswordRandomService(BaseService, NoAuthServiceInterface):
	validator_class= RegeneratePasswordRandomValidator

	def __init__(self, transaction_processor: TransactionProcessorInterface,
		user_manager: ManagerInterface, random_manager: RandomManagerInterface,
		email_sender: EmailSenderInterface):

		self._transaction_processor = transaction_processor
		self._user_manager = user_manager
		self._random_manager = random_manager
		self._email_sender = email_sender

	async def start_service(self, data: dict):
		
		#data.keys() = ['email']
		data['email'] = data['email'].lower()
		self._validate_received_data(data)

		#get the user by email
		user = self._check_not_found(
			await self._user_manager.get({'email':data['email']}),'email')

		#check signup state
		self._check_complete_signup(user.is_complete, True)
		
		#get random
		random = self._check_not_found(
			await self._random_manager.get({'id':user.id, 'flow':'password'}),'random')
		
		#check random expiration
		self._check_random_expiration(random.updated, True, self._random_manager)
		
		transactions_list = []

		#regenerate random
		random_key = self._random_manager.generate_random()
		tran = self._random_manager.update({'id':random.id, 'flow':random.flow}, {'key':random_key})
		transactions_list.extend(tran)

		#send password forget email
		self._email_sender.send_password_forget_email(user.email, random_key)

		#process transactions
		await self._transaction_processor.process(transactions_list)
		
		return {'detail':'random regenerated'}






#_________________________________AUTH_SERVICES___________________________________________________#

#__________________SET_PASSWORD_SERVICE_____________________________#

class SetPasswordService(BaseAuthService, AuthServiceInterface):
	validator_class= SetPasswordValidator

	def __init__(self, user_id, transaction_processor: TransactionProcessorInterface,
		user_manager: ManagerInterface, password_hasher: PasswordHasherInterface):

		self._transaction_processor = transaction_processor
		self._user_id = user_id
		self._user_manager = user_manager
		self._password_hasher = password_hasher
	
	def _validate_received_data(self, data:dict):
		super()._validate_received_data(data)

		if data['password'] == data['new_password']:
			raise HTTPExceptionGenerator(status_code=400,
				detail=HTTPExceptionGenerator.generate_detail(fields=['password', 'new_password'], 
					error_type='equals', msg=war.equals_msg('password','new_password')))

	async def start_service(self, data: dict):
		
		#data.keys() = ['password', 'new_password']
		self._validate_received_data(data)

		#get the user
		user = self._check_not_found(
			await self._user_manager.get({'id':self._user_id}),'user')
		
		#compare passwords and check complete signup
		self._auth_user(user, data['password'], True, self._password_hasher)

		transactions_list = []

		#generating salt
		salt_password = str(self._generate_password_salt())

		#set user password
		tran = self._user_manager.update({'id':user.id}, {'password': data['new_password']+salt_password, 'salt':salt_password})
		transactions_list.extend(tran)

		#process transactions
		await self._transaction_processor.process(transactions_list)

		return {'detail':'password setted'}



#__________________SET_EMAIL_SERVICE_________________________________#

class SetEmailService(BaseAuthService, AuthServiceInterface):
	validator_class= SetEmailValidator

	def __init__(self, user_id, transaction_processor: TransactionProcessorInterface,
		user_manager: ManagerInterface, random_manager: RandomManagerInterface,  
		email_sender: EmailSenderInterface, password_hasher: PasswordHasherInterface):
		
		self._transaction_processor = transaction_processor
		self._user_id = user_id
		self._user_manager = user_manager
		self._random_manager = random_manager
		self._email_sender = email_sender
		self._password_hasher = password_hasher

	async def start_service(self, data: dict):
		
		#data.keys() = ['password', 'new_email']
		data['new_email'] = data['new_email'].lower()
		self._validate_received_data(data)

		result = await asyncio.gather(*[self._user_manager.get({'id':self._user_id}),
			self._random_manager.get({'id':self._user_id, 'flow':'email'}),
			self._user_manager.get({'email':data['new_email']})])

		#get the user
		user = self._check_not_found(result[0],'user')

		#compare passwords and check complete signup
		self._auth_user(user, data['password'], True, self._password_hasher)

		#check if random exist
		self._check_found(result[1],'random')

		#check if new_email exist
		self._check_found(result[2],'new_email')

		transactions_list = []

		#create email random
		random, tran = self._random_manager.create({'id':user.id, 'flow':'email', 'value':data['new_email']})
		transactions_list.extend(tran)

		#send set email
		self._email_sender.send_set_email(random.value, random.key)

		#process transactions
		await self._transaction_processor.process(transactions_list)

		return {'detail':'set email sended'}



#__________________COMPLETE_SET_EMAIL_SERVICE_________________________________#

class CompleteSetEmailService(BaseAuthService, AuthServiceInterface):
	validator_class= CompleteSetEmailValidator

	def __init__(self, user_id, transaction_processor: TransactionProcessorInterface,
		user_manager: ManagerInterface, random_manager: RandomManagerInterface):
		
		self._transaction_processor = transaction_processor
		self._user_id = user_id
		self._user_manager = user_manager
		self._random_manager = random_manager

	async def start_service(self, data: dict):
		
		#data.keys() = ['random']
		self._validate_received_data(data)

		result = await asyncio.gather(*[self._user_manager.get({'id':self._user_id}),
			self._random_manager.get({'id':self._user_id, 'flow':'email'})])
		
		#get the user
		user = self._check_not_found(result[0],'user')

		#get random
		random = self._check_not_found(result[1],'random')
		
		#check random expiration and compare the keys
		self._validate_random(random, data['random'], self._random_manager)

		transactions_list = []

		#set user email
		tran = self._user_manager.update({'id':user.id}, {'email': random.value})
		transactions_list.extend(tran)

		#delete random
		tran = self._random_manager.delete({'id':random.id, 'flow':random.flow})
		transactions_list.extend(tran)

		#process transactions
		await self._transaction_processor.process(transactions_list)

		return {'detail':'email setted'}



#__________________REGENERATE_EMAIL_RANDOM_SERVICE_____________________________#

class RegenerateEmailRandomService(BaseService, AuthServiceInterface):
	validator_class= None

	def __init__(self, user_id, transaction_processor: TransactionProcessorInterface,
		user_manager: ManagerInterface, random_manager: RandomManagerInterface,
		email_sender: EmailSenderInterface):

		self._transaction_processor = transaction_processor
		self._user_id = user_id
		self._user_manager = user_manager
		self._random_manager = random_manager
		self._email_sender = email_sender

	async def start_service(self, data: dict):

		result = await asyncio.gather(*[self._user_manager.get({'id':self._user_id}),
			self._random_manager.get({'id':self._user_id, 'flow':'email'})])

		#get the user
		user = self._check_not_found(result[0],'user')

		#check signup state
		self._check_complete_signup(user.is_complete, True)
		
		#get random
		random = self._check_not_found(result[1],'random')
		
		#check random expiration
		self._check_random_expiration(random.updated, True, self._random_manager)
		
		transactions_list = []

		#regenerate random
		random_key = self._random_manager.generate_random()
		tran = self._random_manager.update({'id':random.id, 'flow':random.flow}, {'key':random_key})
		transactions_list.extend(tran)

		#send set email
		self._email_sender.send_set_email(random.value, random_key)

		#process transactions
		await self._transaction_processor.process(transactions_list)
		
		return {'detail':'random regenerated'}



#_______________________LOGOUT_SERVICE__________________________________________#

class LogoutService(BaseService, AuthServiceInterface):
	validator_class= None

	def __init__(self, user_id, session_id, 
		transaction_processor: TransactionProcessorInterface, 
		user_manager: ManagerInterface, 
		session_manager: RelationalManagerInterface):

		self._transaction_processor = transaction_processor
		self._user_id = user_id
		self._session_id = session_id
		self._user_manager = user_manager
		self._session_manager = session_manager

	async def start_service(self, data: dict):

		result = await asyncio.gather(*[self._user_manager.get({'id':self._user_id}),
			self._session_manager.get({'user_id':self._user_id, 'session_id':self._session_id})])

		#get the user
		user = self._check_not_found(result[0], 'user')

		#check signup state
		self._check_complete_signup(user.is_complete, True)
		
		#get session
		session = self._check_not_found(result[1], 'session')

		transactions_list = []
		
		#delete session
		tran = self._session_manager.delete({'user_id':self._user_id, 'session_id':self._session_id})
		transactions_list.extend(tran)

		#process transactions
		await self._transaction_processor.process(transactions_list)

		return {'detail':'session ended'}


#_______________________GET_USER_DATA_SERVICE__________________________________________#

class GetUserDataService(BaseService, AuthServiceInterface):
	validator_class= None

	def __init__(self, user_id, transaction_processor: TransactionProcessorInterface,
		user_manager: ManagerInterface, user_permission_manager: RelationalManagerInterface,
		user_group_manager: RelationalManagerInterface, session_manager: RelationalManagerInterface):

		self._transaction_processor = transaction_processor
		self._user_id = user_id
		self._user_manager = user_manager
		self._user_permission_manager = user_permission_manager
		self._user_group_manager = user_group_manager
		self._session_manager = session_manager

	async def start_service(self, data: dict):

		#search user, user_permissions and user_group using user_id
		result = await asyncio.gather(*[self._user_manager.get({'id':self._user_id}),
			self._user_permission_manager.get_many_by({'user_id':self._user_id}),
			self._user_group_manager.get_many_by({'user_id':self._user_id}),
			self._session_manager.get_many_by({'user_id':self._user_id})])
		
		#check if the user_id exist
		user =  self._check_not_found(result[0], 'user')
		permissions = []
		groups = []
		sessions = []

		for user_permission in result[1]:
			permissions.append(user_permission.permission_id)

		for user_group in result[2]:
			groups.append(user_group.group_id)

		for session in result[3]:
			sessions.append({'id':session.session_id, 
				'expirated':session.expirated, 'created':session.created})

		user.permissions = permissions
		user.groups = groups
		user.sessions = sessions

		return user


#_______________________SET_USERNAME_SERVICE__________________________________________#

class SetUsernameService(BaseAuthService, AuthServiceInterface):
	validator_class= SetUsernameValidator

	def __init__(self, user_id, transaction_processor: TransactionProcessorInterface,
		user_manager: ManagerInterface, password_hasher: PasswordHasherInterface):

		self._transaction_processor = transaction_processor
		self._user_id = user_id
		self._user_manager = user_manager
		self._password_hasher = password_hasher

	async def start_service(self, data: dict):
		#data.keys() = ['new_username', 'password']
		self._validate_received_data(data)

		#check if the user_id exist
		user = self._check_not_found(await self._user_manager.get({'id': self._user_id}), 'user')
		
		#compare passwords and check complete signup
		self._auth_user(user, data['password'], True, self._password_hasher)

		if user.username == data['new_username']: return {'detail':'username setted'}
		
		#set username
		tran = self._user_manager.update({'id':user.id}, {'username':data['new_username']})
		#process transactions
		await self._transaction_processor.process(tran)

		return {'detail':'username setted'}