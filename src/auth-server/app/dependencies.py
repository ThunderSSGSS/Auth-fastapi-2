import aioredis
from fastapi import Request, Depends, HTTPException
#adapters
from app.internal.adapter.cache import CACHE_URI
from app.internal.adapter.database import SessionLocal, TransactionProcessor
from app.internal.adapter.cruds import (UserCRUD, RandomCRUD, GroupCRUD, 
	PermissionCRUD, UserPermissionCRUD, UserGroupCRUD, GroupPermissionCRUD, LogCRUD,
	SessionCRUD)
from app.internal.adapter.auth import EmailSender, TokenGenerator, PasswordHasher
#managers
from app.internal.domain.managers import (UserManager, RandomManager, PermissionManager,
	GroupManager, UserPermissionManager, UserGroupManager, GroupPermissionManager, LogManager,
	SessionManager)
#services
from app.internal.application.authorization import CheckAuthorizationService
from app.internal.application.services import (SignupService, CompleteSignupService, 
	AuthenticationService, RefreshTokenService, RegenerateSignupRandomService, 
	RegeneratePasswordRandomService, ForgetPasswordService, RestaurePasswordService, 
	SetPasswordService, SetEmailService, CompleteSetEmailService, RegenerateEmailRandomService,
	LogoutService, GetUserDataService, SetUsernameService)
from app.internal.application.admin import(UserCRUDService, PermissionCRUDService, 
	GroupCRUDService, PermissionGrantService, GroupGrantService, SessionManagementService)
#others
from app.internal import warnings as war
from app.internal.settings import RANDOM_EXP, TEST_MODE



async def _get_db_session():
	if TEST_MODE: yield None
	else:
		async with SessionLocal() as asession:
			async with asession.begin():
				yield asession


async def _get_cache_session():
	if TEST_MODE: yield None
	else:
		redis = aioredis.Redis.from_url(CACHE_URI)
		async with redis.client() as asession:
			yield asession


#_____________________INTRA_SERVICE___________________________________#

#_______CHECK_AUTHORIZATION_SERVICE_________#
def get_check_authorization_service():
	token_generator = TokenGenerator()
	return CheckAuthorizationService(token_generator)

def _check_authorization(request: Request, permissions:list, groups:list):
	if 'Authorization' in request.headers:
		service = get_check_authorization_service()
		return service.start_service({'access_token':request.headers['Authorization'],
			'permissions':permissions, 'groups':groups})
	raise HTTPException(status_code=400,  detail='Authorization not provited')


#___________CHECK_PERMISSIONS__________#

#________admins permissions______#
def _check_admin_permission(req: Request):
	return _check_authorization(req,['admin'],[])

#user management permissions
def _check_create_user_permission(req: Request):
	return _check_authorization(req,['create_user'],[])

def _check_read_user_permission(req: Request):
	return _check_authorization(req,['read_user'],[])

def _check_update_user_permission(req: Request):
	return _check_authorization(req,['update_user'],[])

def _check_delete_user_permission(req: Request):
	return _check_authorization(req,['delete_user'],[])

#permissions management permissions
def _check_create_permission_permission(req: Request):
	return _check_authorization(req,['create_permission'],[])

def _check_read_permission_permission(req: Request):
	return _check_authorization(req,['read_permission'],[])

def _check_delete_permission_permission(req: Request):
	return _check_authorization(req,['delete_permission'],[])

#groups management permissions
def _check_create_group_permission(req: Request):
	return _check_authorization(req,['create_group'],[])

def _check_read_group_permission(req: Request):
	return _check_authorization(req,['read_group'],[])

def _check_delete_group_permission(req: Request):
	return _check_authorization(req,['delete_group'],[])

#grant permissions and groups management permissions
def _check_grant_permission_to_permission(req: Request):
	return _check_authorization(req,['grant_permission_to'],[])

def _check_remove_permission_from_permission(req: Request):
	return _check_authorization(req,['remove_permission_from'],[])

def _check_add_user_to_group_permission(req: Request):
	return _check_authorization(req,['add_user_to_group'],[])

def _check_remove_user_from_group_permission(req: Request):
	return _check_authorization(req,['remove_user_from_group'],[])

#session management permissions
def _check_delete_session_permission(req: Request):
	return _check_authorization(req,['delete_session'],[])


#______normal permissions_______#
def _check_set_password_permission(req: Request):
	return _check_authorization(req, ['set_own_password'],[])

def _check_set_username_permission(req: Request):
	return _check_authorization(req, ['set_own_username'],[])

def _check_set_email_permission(req: Request):
	return _check_authorization(req, ['set_own_email'],[])

def _check_logout_permission(req: Request):
	return _check_authorization(req, ['logout'],[])

def _check_read_own_user_data_permission(req: Request):
	return _check_authorization(req, ['read_own_user_data'],[])


#__________________________SERVICES_DEPENDENCES______________________________#

#________AUTHENTICATION_SERVICE__________#
def get_authentication_service(asession=Depends(_get_db_session)):
	log_manager = LogManager(None, LogCRUD(asession))

	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	user_permission_manager = UserPermissionManager(log_manager, UserPermissionCRUD(asession))
	user_group_manager = UserGroupManager(log_manager, UserGroupCRUD(asession))
	group_permission_manager = GroupPermissionManager(log_manager, GroupPermissionCRUD(asession))
	session_manager = SessionManager(log_manager, SessionCRUD(asession))
	token_generator = TokenGenerator()

	return AuthenticationService(transaction_processor, user_manager, user_permission_manager, 
		user_group_manager, group_permission_manager, session_manager, token_generator, password_hasher)


#_________REFRESH_TOKEN_SERVICE_________#
def get_refresh_token_service(asession=Depends(_get_db_session)):
	log_manager = LogManager(None, LogCRUD(asession))

	token_generator = TokenGenerator()
	transaction_processor = TransactionProcessor(asession)
	session_manager = SessionManager(log_manager, SessionCRUD(asession))

	return RefreshTokenService(transaction_processor, session_manager, token_generator)


#________SIGNUP_SERVICE_________________#
def get_signup_service(asession=Depends(_get_db_session)):
	log_manager = LogManager(None, LogCRUD(asession))

	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager,UserCRUD(asession), password_hasher)
	user_group_manager = UserGroupManager(log_manager, UserGroupCRUD(asession))
	random_manager = RandomManager(log_manager, RandomCRUD(asession), RANDOM_EXP)
	email_sender = EmailSender()

	return SignupService(transaction_processor, user_manager, 
		user_group_manager, random_manager, email_sender)


#________COMPLETE_SIGNUP_SERVICE________#
def get_complete_signup_service(asession=Depends(_get_db_session)):
	log_manager = LogManager(None, LogCRUD(asession))
	
	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	random_manager = RandomManager(log_manager, RandomCRUD(asession), RANDOM_EXP)
	user_permission_manager = UserPermissionManager(log_manager, UserPermissionCRUD(asession))
	user_group_manager = UserGroupManager(log_manager, UserGroupCRUD(asession))
	group_permission_manager = GroupPermissionManager(log_manager, GroupPermissionCRUD(asession))
	session_manager = SessionManager(log_manager, SessionCRUD(asession))
	token_generator = TokenGenerator()

	return CompleteSignupService(transaction_processor, user_manager, random_manager, user_permission_manager,
		user_group_manager, group_permission_manager, session_manager, token_generator, password_hasher)


#________REGENERATE_SIGNUP_RANDOM_SERVICE__________#
def get_regenerate_signup_random_service(asession=Depends(_get_db_session)):
	log_manager = LogManager(None, LogCRUD(asession))

	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	random_manager = RandomManager(log_manager, RandomCRUD(asession), RANDOM_EXP)
	email_sender = EmailSender()

	return RegenerateSignupRandomService(transaction_processor, 
		user_manager, random_manager, email_sender)


#________REGENERATE_PASSWORD_RANDOM_SERVICE__________#
def get_regenerate_password_random_service(asession=Depends(_get_db_session)):
	log_manager = LogManager(None, LogCRUD(asession))

	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	random_manager = RandomManager(log_manager, RandomCRUD(asession), RANDOM_EXP)
	email_sender = EmailSender()

	return RegeneratePasswordRandomService(transaction_processor, 
		user_manager, random_manager, email_sender)


#________FORGET_PASSWORD_SERVICE__________#
def get_forget_password_service(asession=Depends(_get_db_session)):
	log_manager = LogManager(None, LogCRUD(asession))

	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	random_manager = RandomManager(log_manager, RandomCRUD(asession), RANDOM_EXP)
	email_sender = EmailSender()

	return ForgetPasswordService(transaction_processor, 
		user_manager, random_manager, email_sender)


#_______RESTAURE_PASSWORD_SERVICE__________#
def get_restaure_password_service(asession=Depends(_get_db_session)):
	log_manager = LogManager(None, LogCRUD(asession))

	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	random_manager = RandomManager(log_manager, RandomCRUD(asession), RANDOM_EXP)

	return RestaurePasswordService(transaction_processor, user_manager, random_manager)


#_______SET_PASSWORD_SERVICE__________#
def get_set_password_service(auth:dict = Depends(_check_set_password_permission), asession=Depends(_get_db_session)):
	user_id = auth['user_id']
	log_manager = LogManager(user_id, LogCRUD(asession))

	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)

	return SetPasswordService(user_id, transaction_processor, user_manager, password_hasher)


#_______SET_EMAIL_SERVICE_____________#
def get_set_email_service(auth:dict = Depends(_check_set_email_permission), asession=Depends(_get_db_session)):
	user_id = auth['user_id']
	log_manager = LogManager(user_id, LogCRUD(asession))

	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	random_manager = RandomManager(log_manager, RandomCRUD(asession), RANDOM_EXP)
	email_sender = EmailSender()

	return SetEmailService(user_id, transaction_processor, user_manager, 
		random_manager, email_sender, password_hasher)


#_______COMPLETE_SET_EMAIL_SERVICE_____________#
def get_complete_set_email_service(auth:dict = Depends(_check_set_email_permission), asession=Depends(_get_db_session)):
	user_id = auth['user_id']
	log_manager = LogManager(user_id, LogCRUD(asession))

	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	random_manager = RandomManager(log_manager, RandomCRUD(asession), RANDOM_EXP)

	return CompleteSetEmailService(user_id, transaction_processor, user_manager, 
		random_manager)


#________REGENERATE_EMAIL_RANDOM_SERVICE__________#
def get_regenerate_email_random_service(auth:dict = Depends(_check_set_email_permission), asession=Depends(_get_db_session)):
	user_id = auth['user_id']
	log_manager = LogManager(user_id, LogCRUD(asession))

	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	random_manager = RandomManager(log_manager, RandomCRUD(asession), RANDOM_EXP)
	email_sender = EmailSender()

	return RegenerateEmailRandomService(user_id, transaction_processor, 
		user_manager, random_manager, email_sender)


#____________LOGOUT_SERVICE________________#
def get_logout_service(auth:dict = Depends(_check_logout_permission), asession=Depends(_get_db_session)):
	user_id = auth['user_id']
	session_id = auth['session_id']
	log_manager = LogManager(user_id, LogCRUD(asession))

	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	session_manager = SessionManager(log_manager, SessionCRUD(asession))

	return LogoutService(user_id, session_id, transaction_processor, 
		user_manager, session_manager)


#____________GET_USER_DATA_SERVICE________________#
def get_user_data_service(auth:dict = Depends(_check_read_own_user_data_permission), asession=Depends(_get_db_session)):
	user_id = auth['user_id']
	log_manager = LogManager(user_id, LogCRUD(asession))
	
	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	user_permission_manager = UserPermissionManager(log_manager, UserPermissionCRUD(asession))
	user_group_manager = UserGroupManager(log_manager, UserGroupCRUD(asession))
	session_manager = SessionManager(log_manager, SessionCRUD(asession))

	return GetUserDataService(user_id, transaction_processor, 
		user_manager, user_permission_manager, user_group_manager, session_manager)


#____________SET_USERNAME_SERVICE________________#
def get_set_username_service(auth:dict = Depends(_check_set_username_permission), asession=Depends(_get_db_session)):
	user_id = auth['user_id']
	log_manager = LogManager(user_id, LogCRUD(asession))
	
	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)

	return SetUsernameService(user_id, transaction_processor, user_manager, password_hasher)



#_________________________ADMIN_CRUD_SERVICES_DEPENDENCES______________________________#

#___________USER_CRUD_SERVICE___________#

def _get_user_crud_service(auth:dict, asession):
	user_id = auth['user_id']
	log_manager = LogManager(user_id, LogCRUD(asession))
	
	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	random_manager = RandomManager(log_manager, RandomCRUD(asession), RANDOM_EXP)
	user_permission_manager = UserPermissionManager(log_manager, UserPermissionCRUD(asession))
	user_group_manager = UserGroupManager(log_manager, UserGroupCRUD(asession))
	session_manager = SessionManager(log_manager, SessionCRUD(asession))
	email_sender = EmailSender()

	return UserCRUDService(user_id, transaction_processor, user_manager, random_manager, 
		user_permission_manager, user_group_manager, session_manager, email_sender)

def get_create_user_service(auth:dict = Depends(_check_create_user_permission), asession=Depends(_get_db_session)):
	return _get_user_crud_service(auth, asession)

def get_read_user_service(auth:dict = Depends(_check_read_user_permission), asession=Depends(_get_db_session)):
	return _get_user_crud_service(auth, asession)

def get_update_user_service(auth:dict = Depends(_check_update_user_permission), asession=Depends(_get_db_session)):
	return _get_user_crud_service(auth, asession)

def get_delete_user_service(auth:dict = Depends(_check_delete_user_permission), asession=Depends(_get_db_session)):
	return _get_user_crud_service(auth, asession)


#__________PERMISSION_CRUD_SERVICE____________#
def _get_permission_crud_service(auth:dict, asession):
	user_id = auth['user_id']
	log_manager = LogManager(user_id, LogCRUD(asession))
	
	transaction_processor = TransactionProcessor(asession)
	permission_manager = PermissionManager(log_manager, PermissionCRUD(asession))
	user_permission_manager = UserPermissionManager(log_manager, UserPermissionCRUD(asession))
	group_permission_manager = GroupPermissionManager(log_manager, GroupPermissionCRUD(asession))

	return PermissionCRUDService(user_id, transaction_processor, permission_manager, 
		user_permission_manager, group_permission_manager)

def get_create_permission_service(auth:dict = Depends(_check_create_permission_permission), asession=Depends(_get_db_session)):
	return _get_permission_crud_service(auth, asession)

def get_read_permission_service(auth:dict = Depends(_check_read_permission_permission), asession=Depends(_get_db_session)):
	return _get_permission_crud_service(auth, asession)

def get_delete_permission_service(auth:dict = Depends(_check_delete_permission_permission), asession=Depends(_get_db_session)):
	return _get_permission_crud_service(auth, asession)


#________GROUP_CRUD_SERVICE________#
def _get_group_crud_service(auth:dict, asession):
	user_id = auth['user_id']
	log_manager = LogManager(user_id, LogCRUD(asession))
	
	transaction_processor = TransactionProcessor(asession)
	group_manager = GroupManager(log_manager, GroupCRUD(asession))
	user_group_manager = UserGroupManager(log_manager, UserGroupCRUD(asession))
	group_permission_manager = GroupPermissionManager(log_manager, GroupPermissionCRUD(asession))

	return GroupCRUDService(user_id, transaction_processor, group_manager, 
		user_group_manager, group_permission_manager)

def get_create_group_service(auth:dict = Depends(_check_create_group_permission), asession=Depends(_get_db_session)):
	return _get_group_crud_service(auth, asession)

def get_read_group_service(auth:dict = Depends(_check_read_group_permission), asession=Depends(_get_db_session)):
	return _get_group_crud_service(auth, asession)

def get_delete_group_service(auth:dict = Depends(_check_delete_group_permission), asession=Depends(_get_db_session)):
	return _get_group_crud_service(auth, asession)


#________________________OTHERS_ADMIN_SERVICES_DEPENDENCES______________________________#

#________PERMISSION_GRANT_SERVICE________#
def _get_permission_grant_service(auth:dict, asession):
	user_id = auth['user_id']
	log_manager = LogManager(user_id, LogCRUD(asession))
	
	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	permission_manager = PermissionManager(log_manager, PermissionCRUD(asession))
	group_manager = GroupManager(log_manager, GroupCRUD(asession))
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	user_permission_manager = UserPermissionManager(log_manager, UserPermissionCRUD(asession))
	group_permission_manager = GroupPermissionManager(log_manager, GroupPermissionCRUD(asession))

	return PermissionGrantService(user_id, transaction_processor, permission_manager, 
		group_manager, user_manager, user_permission_manager, group_permission_manager)

def get_grant_permission_service(auth:dict = Depends(_check_grant_permission_to_permission), asession=Depends(_get_db_session)):
	return _get_permission_grant_service(auth, asession)

def get_remove_permission_service(auth:dict = Depends(_check_remove_permission_from_permission), asession=Depends(_get_db_session)):
	return _get_permission_grant_service(auth, asession)


#________GROUP_GRANT_SERVICE________#
def _get_group_grant_service(auth:dict, asession):
	user_id = auth['user_id']
	log_manager = LogManager(user_id, LogCRUD(asession))
	
	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	group_manager = GroupManager(log_manager, GroupCRUD(asession))
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	user_group_manager = UserGroupManager(log_manager, UserGroupCRUD(asession))

	return GroupGrantService(user_id, transaction_processor, group_manager, 
		user_manager, user_group_manager)

def get_add_user_to_group_service(auth:dict = Depends(_check_add_user_to_group_permission), asession=Depends(_get_db_session)):
	return _get_group_grant_service(auth, asession)

def get_remove_user_from_group_service(auth:dict = Depends(_check_remove_user_from_group_permission), asession=Depends(_get_db_session)):
	return _get_group_grant_service(auth, asession)


#____________SESSION_MANAGEMENT_SERVICE________________#
def _get_session_management_service(auth:dict, asession):
	user_id = auth['user_id']
	log_manager = LogManager(user_id, LogCRUD(asession))

	password_hasher = PasswordHasher()
	transaction_processor = TransactionProcessor(asession)
	user_manager = UserManager(log_manager, UserCRUD(asession), password_hasher)
	session_manager = SessionManager(log_manager, SessionCRUD(asession))

	return SessionManagementService(user_id, transaction_processor, user_manager, 
		session_manager)

def get_delete_session_service(auth:dict = Depends(_check_delete_session_permission), asession=Depends(_get_db_session)):
	return _get_session_management_service(auth, asession)