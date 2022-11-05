from fastapi import HTTPException
from pydantic import ValidationError

#___________________EXCEPTIONS_________________#
class AuthServerException(Exception):
	def __init__(self, value):
		self.value = value

class HTTPExceptionGenerator(HTTPException):
	@classmethod
	def generate_detail(cls, fields:list, error_type:str, msg:str='invalid'):
		data_dict = {'loc':fields, 'msg':msg, 'type':error_type}
		return [data_dict]

class DictValidatorException(ValidationError):
	pass