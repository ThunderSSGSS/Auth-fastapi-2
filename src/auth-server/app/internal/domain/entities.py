import uuid
from datetime import datetime
import abc

class Entity(abc.ABC):
	def __init__(self, **kwargs):
		self.created = kwargs.get('created',datetime.now())
		self.updated = kwargs.get('updated',datetime.now())

	def dict(self):
		data = {}
		for attribute, value in self.__dict__.items():
			if value is not None: data[attribute] = value
		return data
	
	@abc.abstractmethod
	def get_id(self):
		pass


class Random(Entity):
	def __init__(self, **kwargs):
		self.id:uuid.UUID = kwargs['id']
		self.key:str = kwargs['key']
		self.flow:str = kwargs['flow']
		self.value:str = kwargs.get('value')
		super().__init__(**kwargs)
	
	def get_id(self):
		return {'id':self.id, 'flow':self.flow}


class User(Entity):
	def __init__(self, **kwargs):
		self.id:uuid.UUID = kwargs['id']
		self.username:str = kwargs['username']
		self.email:str = kwargs['email']
		self.password:str = kwargs['password']
		self.is_complete:bool = kwargs.get('is_complete',False)
		super().__init__(**kwargs)
	
	def get_id(self):
		return {'id':self.id}


class Permission(Entity):
	def __init__(self, **kwargs):
		self.id:str = kwargs['id']
		self.is_original:bool = kwargs.get('is_original',False)
		super().__init__(**kwargs)
	
	def get_id(self):
		return {'id':self.id}


class Group(Permission):
	pass


class Session(Entity):
	def __init__(self, **kwargs):
		self.user_id:uuid.UUID = kwargs['user_id']
		self.session_id:uuid.UUID = kwargs['session_id']
		self.expirated:datetime = kwargs['expirated']
		super().__init__(**kwargs)
	
	def get_id(self):
		return {'user_id':self.user_id, 
		'session_id':self.session_id}


class UserPermission(Entity):
	def __init__(self, **kwargs):
		self.user_id:uuid.UUID = kwargs['user_id']
		self.permission_id:str = kwargs['permission_id']
		super().__init__(**kwargs)
	
	def get_id(self):
		return {'user_id':self.user_id, 
		'permission_id':self.permission_id}


class UserGroup(Entity):
	def __init__(self, **kwargs):
		self.user_id:uuid.UUID = kwargs['user_id']
		self.group_id:str = kwargs['group_id']
		super().__init__(**kwargs)
	
	def get_id(self):
		return {'user_id':self.user_id, 
		'group_id':self.group_id}


class GroupPermission(Entity):
	def __init__(self, **kwargs):
		self.group_id:str = kwargs['group_id']
		self.permission_id:str = kwargs['permission_id']
		self.is_original:bool = kwargs.get('is_original',False)
		super().__init__(**kwargs)
	
	def get_id(self):
		return {'group_id':self.group_id, 
		'permission_id':self.permission_id}


class Log(Entity):
	def __init__(self, **kwargs):
		self.id:uuid.UUID = kwargs['id']
		self.user_id:uuid.UUID = kwargs.get('user_id')
		self.object_type:str = kwargs['object_type']
		self.object_id:str = kwargs['object_id']
		self.action:str = kwargs['action']
		self.message:str = kwargs.get('message')
		super().__init__(**kwargs)

	def get_id(self):
		return {'id':self.id}