from .database import (StatusTable, GroupTable, PermissionTable, GroupPermissionTable, 
	UserTable, UserPermissionTable)
from sqlalchemy import and_
import uuid


def create_group(db, name:str):
	data = db.query(GroupTable).filter(GroupTable.id == name).first()
	if data is not None: return False
	db.add(GroupTable(id=name, is_original=True))
	return True
	

def create_permission(db, name:str):
	data = db.query(PermissionTable).filter(PermissionTable.id == name).first()
	if data is not None: return False
	db.add(PermissionTable(id=name, is_original=True))
	return True
	

def create_group_permission(db, group:str, permission:str):
	data = db.query(GroupPermissionTable).filter(and_( GroupPermissionTable.group_id == group,
		GroupPermissionTable.permission_id == permission)).first()
	if data is not None: return False
	db.add(GroupPermissionTable(group_id=group,permission_id=permission,is_original=True))
	return True


def _create_admin_user(db, email:str, user_id:uuid.UUID, create_status:bool):
	#check if the email exist
	data = db.query(UserTable).filter(UserTable.email == email).first()
	if data is not None: return False
	
	#creating the user
	user_admin = UserTable(id=user_id, email=email, username='ADMIN', password='nada', is_complete=True)
	db.add(user_admin)

	#creating the status 'admin'
	if create_status: db.add(StatusTable(id='admin', value=str(user_id)))
	
	#creating user_permisssion
	data = db.query(UserPermissionTable).filter(and_( UserPermissionTable.user_id == user_id,
		UserPermissionTable.permission_id == 'admin')).first()
	if data is None: db.add(UserPermissionTable(user_id=user_id, permission_id='admin'))
	return True


def create_admin_user(db, email:str):
	data = db.query(StatusTable).filter(StatusTable.id == 'admin').first()
	#if have admin
	if data is not None:
		user_id = uuid.UUID(data.value)
		data = db.query(UserTable).filter(UserTable.id == user_id).first()
		if data is not None: return False
		return _create_admin_user(db, email, user_id, False)
	else: return _create_admin_user(db, email, uuid.uuid4(), True)