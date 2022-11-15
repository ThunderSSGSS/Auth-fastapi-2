from .celery import app
from .database import SessionLocal
from .cruds import (UserEDIT, RandomEDIT, GroupEDIT, PermissionEDIT, UserPermissionEDIT, 
	UserGroupEDIT, GroupPermissionEDIT, LogEDIT, SessionEDIT)
import uuid


def _create_db_session():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def get_db_session():
	return next(_create_db_session())


def select_crud(tablename):
	if tablename==UserEDIT.model_class.__tablename__:
		return UserEDIT
	elif tablename==RandomEDIT.model_class.__tablename__:
		return RandomEDIT
	elif tablename==GroupEDIT.model_class.__tablename__:
		return GroupEDIT
	elif tablename==PermissionEDIT.model_class.__tablename__:
		return PermissionEDIT
	elif tablename==UserPermissionEDIT.model_class.__tablename__:
		return UserPermissionEDIT
	elif tablename==UserGroupEDIT.model_class.__tablename__:
		return UserGroupEDIT
	elif tablename==GroupPermissionEDIT.model_class.__tablename__:
		return GroupPermissionEDIT
	elif tablename==SessionEDIT.model_class.__tablename__:
		return SessionEDIT
	elif tablename==LogEDIT.model_class.__tablename__:
		return LogEDIT
	else:
		return None


def process_errors(type_error:str, errors:list):
	msg = 'ERROR:'+type_error
	for error in errors:
		msg=msg+'\n'+error
	print(msg)

#________________CRUD_OPERATIONS____________________________#

def create_object(crud, data:dict):
	value = crud.validate_create(data)
	if value: crud.create_object(data)
	else: process_errors('CREATE_ERROR', crud.get_errors())
	return value
		
def update_object(crud, unique_data:dict, new_data:dict):
	value = crud.validate_update(new_data) 
	if value: crud.update_object(unique_data, new_data)
	else: process_errors('UPDATE_ERROR', crud.get_errors())
	return value

def delete_object(crud, unique_data):
	crud.delete_object(unique_data)
	return True

def delete_many_objects_by(crud, repeated_data:dict):
	crud.delete_many_objects_by(repeated_data)
	return True

#____________________TASKS_________________________#

@app.task(name='process_transactions')
def process_transactions(transactions_list):
	session = get_db_session()
	crud_class=None
	crud=None
	transaction_type=None
	setted=False

	for transaction in transactions_list:
		crud_class = select_crud(transaction['tablename'])
		transaction_type = transaction.get('type')

		if crud_class is None: break
		if transaction_type is None: break
		crud = crud_class(session)

		# CREATE
		if transaction_type == 'create':
			setted = create_object(crud, transaction['data'])
			if not setted: break
		
		# UPDATE
		elif transaction_type == 'update':
			setted = update_object(crud, transaction['id'], transaction['data'])
			if not setted: break
		
		# DELETE
		elif transaction_type == 'delete':
			setted = delete_object(crud, transaction['id'])
			if not setted: break
		
		# DELETE_MANY_BY
		elif transaction_type == 'delete_many_by':
			setted = delete_many_objects_by(crud, transaction['id'])
			if not setted: break

	if setted: session.commit()
	session.close()