import json
from app.internal.adapter.interfaces import TokenGeneratorInterface
from .interfaces import IntraServiceInterface

from app.internal.validators import CheckAuthorizationValidator
from app.internal.exceptions import HTTPExceptionGenerator
from app.internal import warnings as war


#_________________________________AUTHORIZATION_________________________________#

class CheckAuthorizationService(IntraServiceInterface):
	validator_class=CheckAuthorizationValidator

	def __init__(self, token_generator: TokenGeneratorInterface):
		self._token_generator = token_generator
	
	def _validate_received_data(self, data:dict):
		try: self.validator_class.validate(data)
		except Exception as ex: raise HTTPExceptionGenerator(status_code=400, detail=json.loads(ex.json()))
	
	def _have_permission(self, decoded_access:dict, permission_name:str):
		for name in decoded_access['permissions']:
			if name == permission_name or name == 'admin': return True
		return False
	
	def _have_group(self, decoded_access:dict, group_name:str):
		for name in decoded_access['groups']:
			if name == group_name: return True
		return False
	
	def _unauthorized_exception(self):
		return HTTPExceptionGenerator(status_code=401,
			detail=HTTPExceptionGenerator.generate_detail(fields=['access_token'],
				error_type='unauthorized', msg=war.unauthorized_msg()))
	
	def start_service(self, data: dict):
		#validate data
		self._validate_received_data(data)
		access_token = data['access_token']

		#check bearer
		bearer = 'Bearer '
		posi = access_token.find(bearer)
		if posi>-1: access_token = access_token[len(bearer)+posi:]

		#decode access token
		decoded_access = self._token_generator.decode_access_token(access_token)

		#check groups
		if data.get('groups') is not None:
			for name in data['groups']:
				if not self._have_group(decoded_access, name): 
					raise self._unauthorized_exception()
		
		#check permissions
		if data.get('permissions') is not None:
			for name in data['permissions']:
				if not self._have_permission(decoded_access, name): 
					raise self._unauthorized_exception()

		return {'user_id':decoded_access['user_id'], 'session_id':decoded_access['sub']}