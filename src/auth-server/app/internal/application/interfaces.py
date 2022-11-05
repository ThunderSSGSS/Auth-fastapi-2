import abc

#___________________________SERVICES_INTEFACES_______________________________#

class ServiceInterface(abc.ABC):

	@abc.abstractmethod
	def _validate_received_data(self, data: dict):
		pass


class AuthServiceInterface(ServiceInterface):

	@abc.abstractmethod
	def start_service(self, data: dict):
		pass


class NoAuthServiceInterface(ServiceInterface):

	@abc.abstractmethod
	def start_service(self, data: dict):
		pass


class IntraServiceInterface(ServiceInterface):

	@abc.abstractmethod
	def start_service(self, data: dict):
		pass


#________________________ADMIN_SERVICES_INTEFACES____________________________#

class AdminCRUDServiceInterface(abc.ABC):

	@abc.abstractmethod
	def create(self, data: dict):
		pass

	@abc.abstractmethod
	def get(self, data: dict):
		pass

	@abc.abstractmethod
	def get_many(self, skip:int=0, limit:int=100):
		pass
	
	@abc.abstractmethod
	def set(self, data: dict):
		pass

	@abc.abstractmethod
	def delete(self, data: dict):
		pass


class AdminPermissionServiceInterface(abc.ABC):

	@abc.abstractmethod
	def grant_permission_to_user(self, data: dict):
		pass
	
	@abc.abstractmethod
	def grant_permission_to_group(self, data: dict):
		pass

	@abc.abstractmethod
	def remove_user_permission(self, data: dict):
		pass

	@abc.abstractmethod
	def remove_group_permission(self, data: dict):
		pass


class AdminGroupServiceInterface(abc.ABC):

	@abc.abstractmethod
	def add_user_to_group(self, data: dict):
		pass
	
	@abc.abstractmethod
	def remove_user_from_group(self, data: dict):
		pass


class AdminSessionServiceInterface(abc.ABC):

	@abc.abstractmethod
	def remove_session(self, data: dict):
		pass