#from typing import , Optional
from typing import Optional, List
from pydantic import BaseModel, validator
from datetime import datetime
import uuid
from app.internal.validators import (validate_email, validate_password, 
    validate_username, validate_name)


#______________________SERVICES_SCHEMAS_______________________________#

#___________AUTHENTICATION_SERVICE_________#
class AuthenticationSchema(BaseModel):
    email:str
    password:str

    #validators
    _validator_email = validator('email', allow_reuse=True)(validate_email)
    _validator_password = validator('password', allow_reuse=True)(validate_password)

#RESPONSE
class AuthenticationResponseSchema(BaseModel):
    access_token:str
    token_type:str
    refresh_token:str

#__________SIGNUP_SERVICE___________________#
class SignupSchema(AuthenticationSchema):
    username:str

    #validators
    _validator_username = validator('username', allow_reuse=True)(validate_username)

#RESPONSE
class SignupResponseSchema(BaseModel):
    id:uuid.UUID
    email:str

#____________LOGOUT_SERVICE____________________#

#RESPONSE
class LogoutResponseSchema(BaseModel):
    detail:str

#________COMPLETE_SIGNUP_SERVICE_____________#
class CompleteSignupSchema(AuthenticationSchema):
    random:str

#RESPONSE
class CompleteSignupResponseSchema(AuthenticationResponseSchema):
    pass

#___________REFRESH_TOKEN_SERVICE_____________#
class RefreshTokenSchema(BaseModel):
    refresh_token: str

#RESPONSE
class RefreshTokenResponseSchema(BaseModel):
    access_token:str
    token_type:str

#________REGENERATE_SIGNUP_RANDOM_SERVICE____________#
class RegenerateSignupRandomSchema(BaseModel):
    email:str

    #validators
    _validator_email = validator('email', allow_reuse=True)(validate_email)

#RESPONSE
class RegenerateSignupRandomResponseSchema(BaseModel):
    detail:str

#________REGENERATE_PASSWORD_RANDOM_SERVICE____________#
class RegeneratePasswordRandomSchema(RegenerateSignupRandomSchema):
    pass

#RESPONSE
class RegeneratePasswordRandomResponseSchema(RegenerateSignupRandomResponseSchema):
    pass

#________FORGET_PASSWORD_SERVICE____________#
class ForgetPasswordSchema(RegenerateSignupRandomSchema):
    pass

#RESPONSE
class ForgetPasswordResponseSchema(RegenerateSignupRandomResponseSchema):
    pass

#________RESTAURE_PASSWORD_SERVICE____________#
class RestaurePasswordSchema(BaseModel):
    email:str
    new_password:str
    random:str

    #validators
    _validator_email = validator('email', allow_reuse=True)(validate_email)
    _validator_password = validator('new_password', allow_reuse=True)(validate_password)

#RESPONSE
class RestaurePasswordResponseSchema(RegenerateSignupRandomResponseSchema):
    pass

#________SET_PASSWORD_SERVICE____________#
class SetPasswordSchema(BaseModel):
    new_password:str
    password:str

    #validators
    _validator_pwds = validator('new_password','password', allow_reuse=True)(validate_password)

#RESPONSE
class SetPasswordResponseSchema(RegenerateSignupRandomResponseSchema):
    pass

#________SET_EMAIL_SERVICE________________#
class SetEmailSchema(BaseModel):
    new_email:str
    password:str

    #validators
    _validator_email = validator('new_email', allow_reuse=True)(validate_email)
    _validator_password = validator('password', allow_reuse=True)(validate_password)

#RESPONSE
class SetEmailResponseSchema(RegenerateSignupRandomResponseSchema):
    pass

#________COMPLETE_SET_EMAIL_SERVICE________________#
class CompleteSetEmailSchema(BaseModel):
    random:str

#RESPONSE
class CompleteSetEmailResponseSchema(RegenerateSignupRandomResponseSchema):
    pass

#________REGENERATE_EMAIL_RANDOM_SERVICE________________#

#RESPONSE
class RegenerateEmailRandomResponseSchema(RegenerateSignupRandomResponseSchema):
    pass


#___________________SET_USERNAME_SERVICE________________#
class SetUsernameSchema(BaseModel):
    new_username:str
    password:str

    #validators
    _validator_username = validator('new_username', allow_reuse=True)(validate_username)
    _validator_password = validator('password', allow_reuse=True)(validate_password)


#RESPONSE
class SetUsernameResponseSchema(RegenerateSignupRandomResponseSchema):
    pass



#___________________________ADMIN_CRUD_SCHEMAS_________________________#

#_______CREATE________#

class CreateUserSchema(BaseModel):
    username:str
    email:str
    password:str
    is_complete:bool

    #validators
    _validator_username = validator('username', allow_reuse=True)(validate_username)
    _validator_email = validator('email', allow_reuse=True)(validate_email)
    _validator_password = validator('password', allow_reuse=True)(validate_password)

class CreatePermissionSchema(BaseModel):
    id:str

    #validators
    _validator_name = validator('id', allow_reuse=True)(validate_name)

class CreateGroupSchema(CreatePermissionSchema):
    pass

#RESPONSE
class CreateUserResponseSchema(BaseModel):
    id:uuid.UUID

#RESPONSE
class CreatePermissionResponseSchema(BaseModel):
    id:str

#RESPONSE
class CreateGroupResponseSchema(CreatePermissionResponseSchema):
    pass

#_________GET________#

#RESPONSE
class UserSchema(BaseModel):
    id:uuid.UUID
    username:str
    email:str
    is_complete:bool
    created:datetime
    updated:datetime

    class Config:
        orm_mode = True

#RESPONSE
class PermissionSchema(BaseModel):
    id:str
    created:datetime
    updated:datetime
    class Config:
        orm_mode = True

#RESPONSE
class GroupSchema(PermissionSchema):
    pass


#RESPONSE
class SessionSchema(BaseModel):
    id:uuid.UUID
    created:datetime
    expirated:datetime

#RESPONSE
class UserSpecificSchema(UserSchema):
    permissions:List[str]
    groups:List[str]
    sessions:List[SessionSchema]

#RESPONSE
class PermissionSpecificSchema(PermissionSchema):
    groups:List[str]

#RESPONSE
class GroupSpecificSchema(GroupSchema):
    permissions:List[str]


#_______SET_________#

class SetUserSchema(BaseModel):
    is_complete:Optional[bool]
    username:Optional[str]

    #validators
    _validator_username = validator('username', allow_reuse=True)(validate_username)

#RESPONSE
class SetUserResponseSchema(BaseModel):
    detail:str

#_______DELETE______#

#RESPONSE
class DeleteUserResponseSchema(SetUserResponseSchema):
    pass

#RESPONSE
class DeletePermissionResponseSchema(DeleteUserResponseSchema):
    pass

#RESPONSE
class DeleteGroupResponseSchema(DeleteUserResponseSchema):
    pass



#__________________________OTHERS_ADMIN__SCHEMAS_________________________#

#_______PERMISSION_GRANT_______#

class GrantPermissionToUserSchema(BaseModel):
    user_id:uuid.UUID
    permission_id:str

    #validators
    _validator_name = validator('permission_id', allow_reuse=True)(validate_name)

class GrantPermissionToGroupSchema(BaseModel):
    group_id:str
    permission_id:str

    #validators
    _validator_name = validator('group_id','permission_id', allow_reuse=True)(validate_name)

class RemoveUserPermissionSchema(GrantPermissionToUserSchema):
    pass

class RemoveGroupPermissionSchema(GrantPermissionToGroupSchema):
    pass

#RESPONSE
class GrantResponseSchema(BaseModel):
    detail:str

#RESPONSE
class RemoveResponseSchema(GrantResponseSchema):
    pass


#_________GROUP_GRANT_______#

class AddUserToGroupSchema(BaseModel):
    user_id:uuid.UUID
    group_id:str

    #validators
    _validator_name = validator('group_id', allow_reuse=True)(validate_name)

class RemoveUserFromGroupSchema(AddUserToGroupSchema):
    pass


#_________SESSION_MANAGEMENT_______#

class RemoveSessionSchema(BaseModel):
    user_id:uuid.UUID
    session_id:Optional[uuid.UUID]


#________________________INTRA_SCHEMAS_______________________________#


#_____PUBLIC_KEY_SCHEMAS_____#
class CheckAuthorizationSchema(BaseModel):
    permissions:Optional[List[str]]=[]
    groups:Optional[List[str]]=[]
    access_token:str

class CheckAuthorizationResponseSchema(BaseModel):
    session_id:str
    user_id:str