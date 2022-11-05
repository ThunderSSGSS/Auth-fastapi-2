import abc
import json
import uuid
import random
from datetime import datetime

#interfaces
from app.internal.adapter.interfaces import (RepositoryInterface, RelationalRepositoryInterface, 
	PasswordHasherInterface)
from .entities import (User, Random, Permission, Group, UserPermission, UserGroup, 
	GroupPermission, Log, Session)
from .transactions import Create, Update, Delete, DeleteManyBy
from .interfaces import ManagerInterface, RandomManagerInterface, RelationalManagerInterface

#others
from app.internal.exceptions import AuthServerException
from app.internal.validators import (CreateUserValidator, UpdateUserValidator, 
    CreateRandomValidator, UpdateRandomValidator, CreatePermissionValidator,
    UpdatePermissionValidator, CreateGroupValidator, UpdateGroupValidator,
    CreateUserPermissionValidator, CreateUserGroupValidator, 
	CreateGroupPermissionValidator, CreateLogValidator, CreateSessionValidator)
from app.internal.settings import TEST_MODE



class BaseManager(ManagerInterface):
	entity_class = None
	validator_create_class = None
	validator_update_class = None

	def __init__(self, repository: RepositoryInterface):
		self._repository = repository

	def _generate_exception(self, error:str):
		raise AuthServerException(error)

	def create(self, data:dict):
		data['updated'] = datetime.now()
		data['created'] = datetime.now()

		if self.validator_create_class is None:
			self._generate_exception('Create validator not defined')
		self.validator_create_class.validate(data)
		
		object = self.entity_class(**data)
		return object, [Create(self._repository.get_tablename(), data)]

	async def get(self, unique_data:dict):
		return await self._repository.find(unique_data)

	async def get_many(self, skip:int=0, limit:int=100):
		return await self._repository.find_many(skip,limit)

	def update(self, unique_data:dict, new_data:dict):
		new_data['updated'] = datetime.now()

		if self.validator_update_class is None:
			self._generate_exception('Update validator not defined')
		self.validator_update_class.validate(new_data)

		return [Update(self._repository.get_tablename(), unique_data, new_data)]

	def delete(self, unique_data:dict):
		return [Delete(self._repository.get_tablename(), unique_data)]


#________________________LOG_MANAGER___________________________________#

class LogManager(BaseManager):
	entity_class = Log
	validator_create_class = CreateLogValidator

	def __init__(self, user_id:uuid.UUID, repository: RepositoryInterface):
		super().__init__(repository)
		self._user_id = user_id
	
	def create(self, data:dict):
		#data.keys() = ['object_type', 'object_id', 'action', 'message']
		data['user_id'] = self._user_id
		data['id'] = uuid.uuid4()
		return super().create(data)



class BaseLoggedManager(BaseManager):

	def __init__(self, log_manager:LogManager, repository: RepositoryInterface):
		super().__init__(repository)
		self._log_manager = log_manager
	
	def _is_json_serializable_types(self, type_obj):
		list_types = [str,None,bool,int,float]
		for t in list_types:
			if type_obj == t: return True
		return False
	
	def _serialize_dict(self, data:dict):
		id = data.copy()
		if 'password' in id: id['password']=''
		
		for key in id.keys():
			if not self._is_json_serializable_types(type(id[key])):
				id[key] = str(id[key])
		return id
	
	def _create_log(self, object_id:dict, action:str, message:dict=None):
		log_dict = {'object_type': self._repository.tablename, 
			'object_id': json.dumps(self._serialize_dict(object_id)), 'action': action}
		if message is not None: 
			log_dict['message'] = json.dumps(self._serialize_dict(message))
		log, transactions_list= self._log_manager.create(log_dict)
		return transactions_list

	def create(self, data:dict):
		entity, transactions_list = super().create(data.copy())
		transactions_list.extend(self._create_log(entity.get_id(), 'C', data))
		return entity, transactions_list

	def update(self, unique_data:dict, new_data:dict):
		transactions_list = super().update(unique_data.copy(), new_data.copy())
		transactions_list.extend(self._create_log(unique_data, 'U', new_data))
		return transactions_list

	def delete(self, unique_data:dict):
		transactions_list = super().delete(unique_data.copy())
		transactions_list.extend(self._create_log(unique_data, 'D'))
		return transactions_list
		


class BaseLoggedRelationalManager(BaseLoggedManager, RelationalManagerInterface):
	def __init__(self, log_manager:LogManager, repository: RelationalRepositoryInterface):
		super().__init__(log_manager, repository)
	
	@abc.abstractmethod
	def _get_dict_by(self, repeated_data:dict):
		pass
	
	async def get_many_by(self, repeated_data:dict):
		return await self._repository.find_many_by(self._get_dict_by(repeated_data))
	
	def delete_many_by(self, repeated_data:dict):
		repeated_data2 = self._get_dict_by(repeated_data)
		transactions_list = [DeleteManyBy(self._repository.get_tablename(), repeated_data2)]
		transactions_list.extend(self._create_log(repeated_data2, 'DM'))
		return transactions_list



#_________________________USER_MANAGER___________________________________#

class UserManager(BaseLoggedManager):
	entity_class = User
	validator_create_class = CreateUserValidator
	validator_update_class = UpdateUserValidator

	def __init__(self, log_manager: LogManager, repository: RepositoryInterface, 
		password_hasher: PasswordHasherInterface):
		
		super().__init__(log_manager,repository)
		self._password_hasher = password_hasher

	def _hash_password(self, password:str):
		return self._password_hasher.hash_password(password)

	def create(self, data:dict):
		#data.keys() = ['email', 'username', 'password'] and ['is_complete']
		data_create = data.copy()
		data_create['password'] = self._hash_password(data['password'])
		data_create['id'] = uuid.uuid4()
		return super().create(data_create)

	async def get(self, unique_data:dict):
		#unique_data.keys() = ['id'] or ['email']	
		if 'id' in unique_data: unique_data = {'id':unique_data['id']}
		else: unique_data = {'email':unique_data['email']}
		return await super().get(unique_data)

	def update(self, unique_data:dict, new_data:dict):
		#unique_data.keys() = ['id']
		#new_data.keys() = ['username'] or ['email'] or ['password']
		new_data2 = new_data.copy()
		if 'password' in new_data: 
			new_data2['password'] = self._hash_password(new_data['password'])
		return super().update(unique_data, new_data2)


#_________________________RANDOM_MANAGER___________________________________#

class RandomManager(BaseLoggedRelationalManager, RandomManagerInterface):
	entity_class = Random
	validator_create_class = CreateRandomValidator
	validator_update_class = UpdateRandomValidator

	def __init__(self, log_manager: LogManager, repository: RelationalRepositoryInterface, 
		expiration_minutes: int):
		
		super().__init__(log_manager, repository)
		self._expiration_minutes = expiration_minutes

	def is_expired(self, updated: datetime):
		difference = datetime.now() - updated
		minutes_passed = difference.total_seconds()/60
		if minutes_passed > self._expiration_minutes: return True
		return False

	def generate_random(self):
		return str(random.randint(11111,99999))

	def create(self, data:dict):
		#data.keys() = ['id', 'flow'] or ['value']
		data_create = data.copy()
		data_create['key'] = self.generate_random()

		if TEST_MODE: data_create['key'] = '12345'
		return super().create(data_create)

	def update(self, unique_data:dict, new_data:dict):
		#unique_data.keys() = ['id', 'flow']
		#new_data.keys() = ['key']
		data = {'key':new_data['key']}
		
		if TEST_MODE: data['key'] = '12345'		
		return super().update(unique_data, data)
	
	def _get_dict_by(self, repeated_data:dict):
		#repeated_data.keys() = ['id'] or ['flow']
		if 'id' in repeated_data: return {'id':repeated_data['id']}
		else: return {'flow':repeated_data['flow']}


#_________________________PERMISSION_MANAGER___________________________________#

class PermissionManager(BaseLoggedManager):
	entity_class = Permission
	validator_create_class = CreatePermissionValidator
	validator_update_class = UpdatePermissionValidator
	#id
	def __init__(self, log_manager: LogManager, repository: RepositoryInterface):
		super().__init__(log_manager, repository)
	
	def create(self, data:dict):
		data2 = data.copy()
		data2['is_original'] = False
		return super().create(data2)
	

#_________________________GROUP_MANAGER___________________________________#

class GroupManager(PermissionManager):
	entity_class = Group
	validator_create_class = CreateGroupValidator
	validator_update_class = UpdateGroupValidator


#_________________________SESSION_MANAGER___________________________________#

class SessionManager(BaseLoggedRelationalManager):
	entity_class = Session
	validator_create_class = CreateSessionValidator

	#session_id user_id
	def __init__(self, log_manager: LogManager, repository: RelationalRepositoryInterface):
		super().__init__(log_manager,repository)
	
	def create(self, data:dict):
		#data.keys() = ['user_id', 'expirated']
		data['session_id'] = uuid.uuid4()
		return super().create(data)

	def _get_dict_by(self, repeated_data:dict):
		#repeated_data.keys() = ['session_id'] or ['user_id']
		if 'user_id' in repeated_data: return {'user_id':repeated_data['user_id']}
		else: return {'session_id':repeated_data['session_id']}


#_________________________USER_PERMISSION_MANAGER___________________________________#

class UserPermissionManager(BaseLoggedRelationalManager):
	entity_class = UserPermission
	validator_create_class = CreateUserPermissionValidator

	#user_id permission_id
	def __init__(self,log_manager: LogManager, repository: RelationalRepositoryInterface):
		super().__init__(log_manager,repository)

	def _get_dict_by(self, repeated_data:dict):
		#repeated_data.keys() = ['user_id'] or ['permission_id']
		if 'user_id' in repeated_data: return {'user_id':repeated_data['user_id']}
		else: return {'permission_id':repeated_data['permission_id']}


#_________________________USER_GROUP_MANAGER___________________________________#

class UserGroupManager(BaseLoggedRelationalManager):
	entity_class = UserGroup
	validator_create_class = CreateUserGroupValidator

	#'user_id', 'group_id'
	def __init__(self, log_manager: LogManager, repository: RelationalRepositoryInterface):
		super().__init__(log_manager, repository)

	def _get_dict_by(self, repeated_data:dict):
		#repeated_data.keys() = ['user_id'] or ['group_id']
		if 'user_id' in repeated_data: return {'user_id':repeated_data['user_id']}
		else: return {'group_id':repeated_data['group_id']}


#_________________________GROUP_ROLE_MANAGER___________________________________#

class GroupPermissionManager(BaseLoggedRelationalManager):
	entity_class = GroupPermission
	validator_create_class = CreateGroupPermissionValidator

	#'group_id', 'permission_id'
	def __init__(self, log_manager: LogManager, repository: RelationalRepositoryInterface):
		super().__init__(log_manager, repository)
	
	def create(self, data:dict):
		data2 = data.copy()
		data2['is_original'] = False
		return super().create(data2)

	def _get_dict_by(self, repeated_data:dict):
		#repeated_data.keys() = ['group_id'] or ['permission_id']
		if 'group_id' in repeated_data: return {'group_id':repeated_data['group_id']}
		else: return {'permission_id':repeated_data['permission_id']}