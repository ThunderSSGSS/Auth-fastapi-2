import uuid
from fastapi import APIRouter, Depends
from app import schemas
#dependencies
from app.dependencies import (get_authentication_service, get_refresh_token_service, 
	get_signup_service, get_regenerate_signup_random_service, get_regenerate_password_random_service,
	get_complete_signup_service, get_forget_password_service, get_restaure_password_service, get_set_password_service,
	get_set_email_service, get_complete_set_email_service, get_regenerate_email_random_service, get_logout_service,
	get_user_data_service, get_set_username_service)
#interfaces
from app.internal.application.interfaces import AuthServiceInterface, NoAuthServiceInterface


# routers
router_signup = APIRouter(tags=['Auth: signup flow'])
router_authenticate = APIRouter(tags=['Auth: authenticate, refresh and logout'])
router_forget_password = APIRouter(tags=['Auth: forget password flow'])
router_set_email = APIRouter(tags=['Auth: set email flow'])
router_others = APIRouter(tags=['Auth: others routers'])


#_____________SIGNUP____________#
@router_signup.post("/signup", response_model=schemas.SignupResponseSchema)
async def signup(data: schemas.SignupSchema, 
	service: NoAuthServiceInterface = Depends(get_signup_service)):
	"""
		## Signup
		This route will:<br>
		* create a user;<br>
		* add the created user to the *normal* group;<br>
		* send a random code to the user email to complete the signup.<br>
		<p><b>Note</b>: the random code expires.</p>
		<p><b>Return</b>: user id and email.</p>
	"""
	return await service.start_service(data.dict())


#________COMPLETE_SIGNUP________#
@router_signup.post("/signup/complete", response_model=schemas.CompleteSignupResponseSchema)
async def complete_signup(data: schemas.CompleteSignupSchema, 
	service: NoAuthServiceInterface = Depends(get_complete_signup_service)):
	"""
		## Complete signup
		This route will set the user status (is_complete=true) and authenticate.
		<p><b>Note</b>: *random* is the code sended to user email. If the random is expired will return an error.</p>
		<p><b>Return</b>: access token and refresh token</p>
	"""
	return await service.start_service(data.dict())


#___________REGENERATE_SIGNUP_RANDOM___________#
@router_signup.post("/random/regenerate/signup", response_model=schemas.RegenerateSignupRandomResponseSchema)
async def regenerate_signup_random(data: schemas.RegenerateSignupRandomSchema, 
	service: NoAuthServiceInterface = Depends(get_regenerate_signup_random_service)):
	"""
		## Regenerate Signup Random
		This route will: regenerate the signup random code and send to email. 
		<p><b>Note</b>: For security, if the signup random is not expired will return an error.</p>
	"""
	return await service.start_service(data.dict())


#_______AUTHENTICATION________#
@router_authenticate.post("/authenticate", response_model=schemas.AuthenticationResponseSchema)
async def authenticate_user(data: schemas.AuthenticationSchema,
	service: NoAuthServiceInterface = Depends(get_authentication_service)):
	"""
		## Authenticate
		This route will authenticate the user.
		<p><b>Note</b>: If the user don't complete the signup will return an error</p>
		<p><b>Return</b>: access token and refresh token</p>
	"""
	return await service.start_service(data.dict())


#_______REFRESH_TOKEN________#
@router_authenticate.post("/refresh", response_model=schemas.RefreshTokenResponseSchema)
async def refresh_token(data: schemas.RefreshTokenSchema, 
	service: NoAuthServiceInterface = Depends(get_refresh_token_service)):
	"""
		## Refresh Token
		This route will refresh token.
		<p><b>Note</b>: If the user session don't exist (or was deleted), will return an error</p>
		<p><b>Return</b>: access token</p>
	"""
	return await service.start_service(data.dict())

#___________LOGOUT___________#
@router_authenticate.post("/logout", response_model=schemas.LogoutResponseSchema)
async def logout(service: AuthServiceInterface = Depends(get_logout_service)):
	"""
		## Logout
		This route will delete the user session.
		<p><b>Note</b>: After logout, the session refresh token wan't work anymore, but the access token will work until expire.</p>
	"""
	return await service.start_service(None)


#______FORGET_PASSWORD__________#
@router_forget_password.post("/password/forget", response_model=schemas.ForgetPasswordResponseSchema)
async def forget_password(data: schemas.ForgetPasswordSchema,
	service: NoAuthServiceInterface = Depends(get_forget_password_service)):
	"""
		## Forget password (pass 1 of the forget password flow)
		This route will send a random code to the user email.
		<p><b>Note</b>: For security, if the user don't complete the forget password flow will return an error.</p>
	"""
	return await service.start_service(data.dict())


#______RESTAURE_PASSWORD__________#
@router_forget_password.post("/password/restaure", response_model=schemas.RestaurePasswordResponseSchema)
async def restaure_password(data: schemas.RestaurePasswordSchema,
	service: NoAuthServiceInterface = Depends(get_restaure_password_service)):
	"""
		## Restaure (final pass of the forget password flow)
		This route will set the user password.
		<p><b>Note</b>: If the *random* is expired will return an error.</p>
	"""
	return await service.start_service(data.dict())


#___________REGENERATE_PASSWORD_RANDOM___________#
@router_forget_password.post("/random/regenerate/password", response_model=schemas.RegeneratePasswordRandomResponseSchema)
async def regenerate_password_random(data: schemas.RegeneratePasswordRandomSchema, 
	service: NoAuthServiceInterface = Depends(get_regenerate_password_random_service)):
	"""
		## Regenerate Password Random
		This route will regenerate the forget password random code and send to email.
		<p><b>Note</b>: For security, if the *random* is not expired will return an error.</p>
	"""
	return await service.start_service(data.dict())


#_______SET_EMAIL_____________#
@router_set_email.post("/email/set", response_model=schemas.SetEmailResponseSchema)
async def set_email(data: schemas.SetEmailSchema,
	service: AuthServiceInterface = Depends(get_set_email_service)):
	"""
		## Set email (pass 1 of the set email flow)
		This route will send a random code to the new email.
		<p><b>Note</b>: For security, if the user don't complete the set email flow will return an error.</p>
	"""
	return await service.start_service(data.dict())


#_______COMPLETE_SET_EMAIL_____________#
@router_set_email.post("/email/set/complete", response_model=schemas.CompleteSetEmailResponseSchema)
async def complete_set_email(data: schemas.CompleteSetEmailSchema,
	service: AuthServiceInterface = Depends(get_complete_set_email_service)):
	"""
		## Complete set email (final pass of the set email flow)
		This route will set the user email.
		<p><b>Note</b>: If the *random* is expired will return an error.</p>
	"""
	return await service.start_service(data.dict())


#___________REGENERATE_EMAIL_RANDOM___________#
@router_set_email.post("/random/regenerate/email", response_model=schemas.RegenerateEmailRandomResponseSchema)
async def regenerate_email_random(service: AuthServiceInterface = Depends(get_regenerate_email_random_service)):
	"""
		## Regenerate email Random
		This route will regenerate the set email random code and send to email.
		<p><b>Note</b>: For security, if the *random* is not expired will return an error.</p>
	"""
	return await service.start_service(None)


#_______SET_PASSWORD__________#
@router_others.post("/password/set", response_model=schemas.SetPasswordResponseSchema)
async def set_password(data: schemas.SetPasswordSchema,
	service: AuthServiceInterface = Depends(get_set_password_service)):
	"""
		## Set Password
		This route will set the user email.
	"""
	return await service.start_service(data.dict())


#___________GET_USER_DATA____________________#
@router_others.get("/user/data", response_model=schemas.UserSpecificSchema)
async def get_user_data(service: AuthServiceInterface = Depends(get_user_data_service)):
	"""
		## Get User Data
		This route will return user data, permissions, groups and sessions.
	"""
	return await service.start_service(None)


#___________SET_USERNAME________________________#
@router_others.post("/username/set", response_model=schemas.SetUsernameResponseSchema)
async def set_username(data: schemas.SetUsernameSchema,
	service: AuthServiceInterface = Depends(get_set_username_service)):
	"""
		## Set Username
		This route will set the username.
	"""
	return await service.start_service(data.dict())