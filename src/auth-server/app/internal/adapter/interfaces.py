import abc

#internal
from app.internal.domain.entities import Entity


#______________________REPOSITORY_INTEFACES______________________#
class RepositoryInterface(abc.ABC):
	
	@abc.abstractmethod
	def find(self, unique_data: dict):
		pass

	@abc.abstractmethod
	def find_many(self, skip:int=0, limit:int=100):
		pass
	
	@abc.abstractmethod
	def get_tablename(self):
		pass


class RelationalRepositoryInterface(RepositoryInterface):

	@abc.abstractmethod
	def find_many_by(self, repeated_data: dict):
		pass


class CacheRepositoryInterface(abc.ABC):

	@abc.abstractmethod
	def get(self, key: str):
		pass
	
	@abc.abstractmethod
	def set(self, key: str, value, expire:float=0):
		pass
	
	@abc.abstractmethod
	def delete(self, key: str):
		pass

#______________TRANSACTIONS_PROCESSOR_INTEFACES_____________#

class TransactionProcessorInterface(abc.ABC):
	@abc.abstractmethod
	def process(self, transactions_list:list):
		pass

#____________________TOKEN_GENERATOR________________________#
class TokenGeneratorInterface(abc.ABC):
	@abc.abstractmethod
	def create_tokens(self, user_infos: dict):
		pass

	@abc.abstractmethod
	def create_access_token(self, decoded_refresh_token: dict):
		pass

	@abc.abstractmethod
	def decode_refresh_token(self, refresh_token:str):
		pass

	@abc.abstractmethod
	def decode_access_token(self, access_token:str):
		pass

	@abc.abstractmethod
	def get_next_expirated(self):
		pass


#____________________PASSWORD_HASHER_INTERFACE______________________#
class PasswordHasherInterface(abc.ABC):
	@abc.abstractmethod
	def hash_password(self, password: str):
		pass

	@abc.abstractmethod
	def compare_passwords(self, password:str, hashed_password:str):
		pass


#____________________EMAIL_SENDER__________________________#
class EmailSenderInterface(abc.ABC):
	@abc.abstractmethod
	def send_signup_email(self, to:str, random_key:str, data:dict):
		pass

	@abc.abstractmethod
	def send_password_forget_email(self, to:str, random_key:str, data:dict):
		pass
	
	@abc.abstractmethod
	def send_set_email(self, to:str, random_key:str, data:dict):
		pass