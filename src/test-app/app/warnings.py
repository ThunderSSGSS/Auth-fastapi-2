def not_found_msg(model_name:str):
	return model_name+' not found'

def deleted_msg(model_name:str, id:str):
	return model_name+' '+id+' was deleted'

def altered_msg(model_name:str, id:str):
	return model_name+' '+id+' was altered'

def exist_msg(model_name:str):
	return model_name+' alread exist'