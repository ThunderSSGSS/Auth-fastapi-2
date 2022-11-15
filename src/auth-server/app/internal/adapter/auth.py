import uuid
#jwt
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
#password hash
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from datetime import datetime, timedelta
#Adapters Interfaces
from .interfaces import EmailSenderInterface, PasswordHasherInterface, TokenGeneratorInterface
#celery
from .tasks_celery import send_signup_email, send_password_forget_email, send_set_email
#others
from app.internal.settings import AUTH, TEST_MODE
from app.internal import warnings as war
from app.internal.validators import ToEncodeValidator, DecodedValidator
from app.internal.exceptions import AuthServerException, HTTPExceptionGenerator
#AES
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode


#__________________________GLOBALS___________________________________#

_ALGORITHM = AUTH['JWT_ALGORITHM']
_PUBLIC_KEY = AUTH['PUBLIC_KEY']
_PRIVATE_KEY = AUTH['PRIVATE_KEY']

_SECRET_KEY = AUTH['SECRET_KEY']

_ACCESS_TOKEN_EXP = int(AUTH['ACCESS_TOKEN_EXP'])
_REFRESH_TOKEN_EXP = int(AUTH['REFRESH_TOKEN_EXP'])

#AES_CBC
_IV_access_token= _SECRET_KEY[0:16].encode()
_IV_refresh_token= _SECRET_KEY[16:32].encode()
_SECRET_KEY_encoded = _SECRET_KEY.encode()


#____EXCEPTION____#

def _token_expired_exception(name:str):
	return HTTPExceptionGenerator(status_code=403,
		detail=HTTPExceptionGenerator.generate_detail(fields=[name], 
			error_type='expired', msg=war.expired_msg(name)))

def _token_invalid_exception(name:str, error_type='invalid'):
	return HTTPExceptionGenerator(status_code=403,
		detail=HTTPExceptionGenerator.generate_detail(fields=[name], 
			error_type=error_type, msg=war.invalid_msg(name)))

def _token_not_provited_exception(name:str):
	return HTTPExceptionGenerator(status_code=400,
		detail=HTTPExceptionGenerator.generate_detail(fields=[name], 
			error_type='not_provited', msg=war.not_provited_msg(name)))

def _unauthorized_exception(name:str):
	return HTTPExceptionGenerator(status_code=401,
		detail=HTTPExceptionGenerator.generate_detail(fields=[name],
			error_type='unauthorized', msg=war.unauthorized_msg()))


#_________________________PASSWORD_HASH______________________________#

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _verify_password(plain_password:str, hashed_password:str):
	try: return _pwd_context.verify(plain_password, hashed_password)
	except UnknownHashError: return False

def _hash_password(password:str):
    return _pwd_context.hash(password)


#_________________________AES_ENCRYPTION________________________________#

def _encrypt_AES(plaintext:str, is_access_token:bool, key_bytes=_SECRET_KEY_encoded):
	iv = _IV_access_token
	if not is_access_token: iv= _IV_refresh_token
	cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
	return b64encode(cipher.encrypt(pad(plaintext.encode(),16))).decode()

def _decrypt_AES(ciphertext:str, is_access_token:bool, key_bytes=_SECRET_KEY_encoded):
	iv = _IV_access_token
	if not is_access_token: iv= _IV_refresh_token
	cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
	try: return unpad(cipher.decrypt(b64decode(ciphertext.encode())),16).decode()
	except:
		if is_access_token: raise _token_invalid_exception('access_token')
		else: raise _token_invalid_exception('refresh_token')



#______________________________JWT______________________________________#

#____VALIDATION____#

def __validate(validator_class, data:dict, validate_access_token:bool):
	if validator_class.is_valid(data):
		if validate_access_token: return validator_class.is_access_token(data)
		else: return validator_class.is_refresh_token(data)
	return False

def _validate_decoded(decoded: dict, validate_access_token:bool=True):
	return __validate(DecodedValidator, decoded, validate_access_token)

def _validate_to_encode(to_encode: dict, validate_access_token:bool=True):
	return __validate(ToEncodeValidator, to_encode, validate_access_token)


#____OPERATIONS____#

def _create_tokens(to_encode:dict, access_token_exp:int = _ACCESS_TOKEN_EXP,
	refresh_token_exp:int = _REFRESH_TOKEN_EXP, private_key:str = _PRIVATE_KEY, 
	algorithm:str = _ALGORITHM):
	"""
	This function is used to create tokens (access_token and refresh_token)
	"""
	#setting the expiration time of access token
	to_encode['exp'] = datetime.utcnow() + timedelta(minutes=access_token_exp)
	to_encode['token_type'] = 'access'

	if not _validate_to_encode(to_encode):
		raise AuthServerException('To encode access dictionary invalid!')
	
	#creating access token
	access_token = jwt.encode(to_encode, private_key, algorithm=algorithm)
		
	#setting the expiration time of refresh token
	to_encode['exp']= datetime.utcnow() + timedelta(minutes=refresh_token_exp)
	to_encode['token_type'] = 'refresh'

	if not _validate_to_encode(to_encode,False):
		raise AuthServerException('To encode refresh dictionary invalid!')
	
	#creating refresh token
	refresh_token = jwt.encode(to_encode, private_key, algorithm=algorithm)

	return {'access_token':access_token, 'token_type':'bearer', 'refresh_token':refresh_token}
	


def _decode_token(token:str, is_access:bool=True, public_key:str = _PUBLIC_KEY, algorithm:str = _ALGORITHM):
	token_name='access_token'
	if not is_access: token_name = 'refresh_token'
	try:
		decoded_token = jwt.decode(token, public_key, algorithms=[algorithm])
		
		#validate the decoded data
		if not _validate_decoded(decoded_token, is_access):
			raise _token_invalid_exception(token_name, 'forbidden')
		return decoded_token
	
	except ExpiredSignatureError: raise _token_expired_exception(token_name)
	except JWTError: raise _token_invalid_exception(token_name)


def _create_access_token(decoded_refresh_token:dict, private_key:str = _PRIVATE_KEY,
	access_token_exp:int = _ACCESS_TOKEN_EXP, algorithm:str = _ALGORITHM):

	#validate the decoded data
	if not _validate_decoded(decoded_refresh_token,False):
		raise _token_invalid_exception('refresh_token', 'forbidden')
	to_encode = decoded_refresh_token

	#setting expiration time of access token
	to_encode['exp'] = datetime.utcnow() + timedelta(minutes=access_token_exp)
	to_encode['token_type'] = 'access'

	if not _validate_to_encode(to_encode):
		raise AuthServerException('To encode access dictionary invalid!')

	#creating new access_token
	access_token = jwt.encode(to_encode, private_key, algorithm=algorithm)
	return {'access_token':access_token, 'token_type':'bearer'}



#______________________ADAPTERS_______________________________________#

class EmailSender(EmailSenderInterface):

	def send_signup_email(self, to:str, random_key:str, data:dict=None):
		if not TEST_MODE: send_signup_email.delay(to, random_key, data)

	def send_password_forget_email(self, to:str, random_key:str, data:dict=None):
		if not TEST_MODE: send_password_forget_email.delay(to, random_key, data)

	def send_set_email(self, to:str, random_key:str, data:dict=None):
		if not TEST_MODE: send_set_email.delay(to, random_key, data)


class TokenGenerator(TokenGeneratorInterface):

	#_______AES____________#
	def _decode_AES(self, token:str, is_access_token:bool):
		return _decrypt_AES(token, is_access_token)

	def _encode_AES(self, token:str, is_access_token:bool):
		return _encrypt_AES(token, is_access_token)
	#_________#

	#_______CREATE___________#

	def create_tokens(self, user_infos: dict):
		token_dict = _create_tokens(user_infos)
		token_dict['access_token'] = self._encode_AES(token_dict['access_token'], True)
		token_dict['refresh_token'] = self._encode_AES(token_dict['refresh_token'], False)
		return token_dict
	
	def create_access_token(self, decoded_refresh_token:dict):
		access_token_dict = _create_access_token(decoded_refresh_token)
		access_token_dict['access_token'] = self._encode_AES(access_token_dict['access_token'], True)
		return access_token_dict

	#_______DECODE___________#

	def decode_refresh_token(self, refresh_token: str):
		refresh_token = self._decode_AES(refresh_token, False)
		return _decode_token(refresh_token,False)
	
	def decode_access_token(self, access_token:str):
		access_token = self._decode_AES(access_token, True)
		return _decode_token(access_token)
	
	def get_next_expirated(self):
		exp = _REFRESH_TOKEN_EXP + _ACCESS_TOKEN_EXP
		return datetime.utcnow() + timedelta(minutes=exp)


class PasswordHasher(PasswordHasherInterface):

	def hash_password(self, password: str):
		return _hash_password(password)

	def compare_passwords(self, password:str, hashed_password:str):
		return _verify_password(password, hashed_password)