def not_found_msg(model_name:str):
	return model_name+' not found'

def deleted_msg(model_name:str, id:str):
	return model_name+' '+id+' was deleted'

def delete_error_msg(model_name:str):
	return 'the selected '+model_name+' can\'t be deleted'

def altered_msg(model_name:str, id:str):
	return model_name+' '+id+' was altered'

def exist_msg(model_name:str):
	return model_name+' alread exist'

def incorrect_msg(model_name:str):
	return 'Incorrect '+model_name

def incorrect_password_msg():
	return incorrect_msg('password')

def expired_msg(model_name:str, expired=True):
	if expired: return model_name+' expired'
	else: return model_name+' is not expired'



#_____Authentication____#
def forbidden_refresh_msg():
	return 'Forbidden, invalid refresh token'

def forbidden_refresh_exp_msg():
	return 'Forbidden, refresh token expired'

def complete_signup_msg(is_complete:bool):
	if is_complete: return 'The user alread complete the signup'
	else: return 'The user dont complete the signup'

#______Authorization____#
def unauthorized_msg():
	return 'Unauthorized'

def auth_not_provited_msg():
	return 'Authentication not provited'



def forbidden_access_msg():
	return 'Forbidden, invalid access token'

def forbidden_access_exp_msg():
	return 'Forbidden, access token expired'


########__VALIDATORS__#########
def not_provited_msg(model_name:str):
	return model_name+' not provited'
	
def invalid_msg(model_name:str):
	return 'The '+model_name+' is invalid'

def invalid_email_msg():
	return invalid_msg('email')

def invalid_password_msg():
	return invalid_msg('password')

def equals_msg(model1:str, model2:str):
	return model1+' and '+model2+' are equals'

def not_equals_msg(model1:str, model2:str):
	return model1+' and '+model2+' are not equals'