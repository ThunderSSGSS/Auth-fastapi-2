import abc
from datetime import datetime




#________________________MANAGERS_INTERFACES______________________________#
class ManagerInterface(abc.ABC):

	@abc.abstractmethod
	def create(self, data: dict):
		pass

	@abc.abstractmethod
	def get(self, unique_data:dict):
		pass

	@abc.abstractmethod
	def get_many(self, skip:int=0, limit:int=100):
		pass

	@abc.abstractmethod
	def update(self, unique_data: dict, new_data: dict):
		pass

	@abc.abstractmethod
	def delete(self, unique_data: dict):
		pass


class RelationalManagerInterface(ManagerInterface):
	@abc.abstractmethod
	def get_many_by(self, repeated_data:dict):
		pass
	
	@abc.abstractmethod
	def delete_many_by(self, repeated_data:dict):
		pass


class RandomManagerInterface(RelationalManagerInterface):
	@abc.abstractmethod
	def is_expired(self, updated:datetime):
		pass
		
	@abc.abstractmethod
	def generate_random(self):
		pass