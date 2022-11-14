import uuid
from fastapi import APIRouter, Depends
from app import schemas
from typing import List
#dependencies
from app.dependencies import (get_create_user_service, get_read_user_service,
	get_update_user_service, get_delete_user_service, get_create_permission_service,
	get_read_permission_service, get_delete_permission_service, get_create_group_service,
	get_read_group_service, get_delete_group_service, get_grant_permission_service,
	get_remove_permission_service, get_add_user_to_group_service, get_remove_user_from_group_service,
	get_delete_session_service)
#interfaces
from app.internal.application.interfaces import (AdminCRUDServiceInterface, AdminPermissionServiceInterface,
	AdminGroupServiceInterface, AdminSessionServiceInterface)



# routers
router_user_crud = APIRouter(tags=['Admin: user CRUD'])
router_permission_crud = APIRouter(tags=['Admin: permission CRUD'])
router_group_crud = APIRouter(tags=['Admin: group CRUD'])
router_grant_permission = APIRouter(tags=['Admin: permission grant'])
router_grant_group = APIRouter(tags=['Admin: group grant'])
router_session_mng = APIRouter(tags=['Admin: session management'])


#_________________________________CRUD_ROUTERS_______________________________#

#______________USERS______________#

#___CREATE___#

@router_user_crud.post("/users", response_model=schemas.CreateUserResponseSchema, status_code=201)
async def create_user(data: schemas.CreateUserSchema, service: AdminCRUDServiceInterface = Depends(get_create_user_service)):
	"""
		## Create User
		This route will create a user.
		<p><b>Note</b>: If *is_complete=true*, the created user don't need complete signup.<br>
		If *is_complete=false*, will create a signup random code and send to created user email, so that the user needs to complete signup.</p>
		<p><b>Note2</b>: The created user don't have any permission or group.</p>
		<p><b>Note3</b>: To use this route the user must have the permission 'create_user' or 'admin'.</p>
		<p><b>Return</b>: the user id</p>
	"""
	return await service.create(data.dict())

#_____GET_____#

@router_user_crud.get("/users", response_model=List[schemas.UserSchema])
async def get_users(skip:int=0, limit:int=100, service: AdminCRUDServiceInterface = Depends(get_read_user_service)):
	"""
		## Get Users
		This route will return a list of users.
		<p><b>Note</b>: To use this route the user must have the permission 'read_user' or 'admin'.</p>
	"""
	return await service.get_many(skip,limit)

@router_user_crud.get("/users/{id}", response_model=schemas.UserSpecificSchema)
async def get_user(id: uuid.UUID, service: AdminCRUDServiceInterface = Depends(get_read_user_service)):
	"""
		## Get User
		This route will return a specific user data, permissions, groups and sessions.
		<p><b>Note</b>: To use this route the user must have the permission 'read_user' or 'admin'.</p>
	"""
	return await service.get({'id':id})

#_____UPDATE___#

@router_user_crud.put("/users/{id}", response_model=schemas.SetUserResponseSchema)
async def set_user(data: schemas.SetUserSchema, id: uuid.UUID, 
	service: AdminCRUDServiceInterface = Depends(get_update_user_service)):
	"""
		## Set User
		This route will set the user username or signup status.
		<p><b>Note</b>: To use this route the user must have the permission 'read_user' or 'admin'.</p>
		<p><b>Note2</b>: You can use *is_complete=true* to complete user signup. When the user completed the signup, *is_complete=false* will block the user.</p>
	"""
	data_dict = data.dict()
	data_dict['id'] = id
	return await service.set(data_dict)

#____DELETE____#

@router_user_crud.delete("/users/{id}", response_model=schemas.DeleteUserResponseSchema)
async def delete_user(id: uuid.UUID, service: AdminCRUDServiceInterface = Depends(get_delete_user_service)):
	"""
		## Delete User
		This route will delete the user.
		<p><b>Note</b>: To use this route the user must have the permission 'delete_user' or 'admin'.</p>
	"""
	return await service.delete({'id':id})


#______________PERMISSION______________#

#___CREATE___#

@router_permission_crud.post("/permissions", response_model=schemas.CreatePermissionResponseSchema, status_code=201)
async def create_permission(data: schemas.CreatePermissionSchema, service: AdminCRUDServiceInterface = Depends(get_create_permission_service)):
	"""
		## Create Permission
		This route will create a permission.
		<p><b>Note</b>: To use this route the user must have the permission 'create_permission' or 'admin'.</p>
		<p><b>Note2</b>: The *id* is the name of the permission, can't have spaces and special chars. If you want use space use '_'.</p>
		<p><b>Return</b>: the permission id</p>
	"""
	return await service.create(data.dict())

#_____GET_____#

@router_permission_crud.get("/permissions", response_model=List[schemas.PermissionSchema])
async def get_permissions(skip:int=0, limit:int=100, service: AdminCRUDServiceInterface = Depends(get_read_permission_service)):
	"""
		## Get Permissions
		This route will return a list of permissions.
		<p><b>Note</b>: To use this route the user must have the permission 'read_permission' or 'admin'.</p>
	"""
	return await service.get_many(skip,limit)

@router_permission_crud.get("/permissions/{id}", response_model=schemas.PermissionSpecificSchema)
async def get_permission(id: str, service: AdminCRUDServiceInterface = Depends(get_read_permission_service)):
	"""
		## Get Permission
		This route will return a specific permission data and groups that have the permission.
		<p><b>Note</b>: To use this route the user must have the permission 'read_permission' or 'admin'.</p>
	"""
	return await service.get({'id':id})

#____DELETE____#

@router_permission_crud.delete("/permissions/{id}", response_model=schemas.DeletePermissionResponseSchema)
async def delete_permission(id: str, service: AdminCRUDServiceInterface = Depends(get_delete_permission_service)):
	"""
		## Delete Permission
		This route will delete a specific permission.
		<p><b>Note</b>: To use this route the user must have the permission 'delete_permission' or 'admin'.</p>
		<p><b>Note2</b>: The original permissions can't be deleted, if you try will return an error.</p>
	"""
	return await service.delete({'id':id})


#_________________GROUP_________________#

#___CREATE___#

@router_group_crud.post("/groups", response_model=schemas.CreateGroupResponseSchema, status_code=201)
async def create_group(data: schemas.CreateGroupSchema, service: AdminCRUDServiceInterface = Depends(get_create_group_service)):
	"""
		## Create Group
		This route will create a Group.
		<p><b>Note</b>: To use this route the user must have the permission 'create_group' or 'admin'.</p>
		<p><b>Note2</b>: The *id* is the name of the group, can't have spaces and special chars. If you want use space use '_'.</p>
		<p><b>Return</b>: the group id</p>
	"""
	return await service.create(data.dict())

#_____GET_____#

@router_group_crud.get("/groups", response_model=List[schemas.GroupSchema])
async def get_groups(skip:int=0, limit:int=100, service: AdminCRUDServiceInterface = Depends(get_read_group_service)):
	"""
		## Get Groups
		This route will return a list of groups.
		<p><b>Note</b>: To use this route the user must have the permission 'read_group' or 'admin'.</p>
	"""
	return await service.get_many(skip,limit)

@router_group_crud.get("/groups/{id}", response_model=schemas.GroupSpecificSchema)
async def get_group(id: str, service: AdminCRUDServiceInterface = Depends(get_read_group_service)):
	"""
		## Get Group
		This route will return a specific group data and permissions that was granted.
		<p><b>Note</b>: To use this route the user must have the permission 'read_group' or 'admin'.</p>
	"""
	return await service.get({'id':id})

#____DELETE____#

@router_group_crud.delete("/groups/{id}", response_model=schemas.DeleteGroupResponseSchema)
async def delete_group(id: str, service: AdminCRUDServiceInterface = Depends(get_delete_group_service)):
	"""
		## Delete Group
		This route will delete a specific group.
		<p><b>Note</b>: To use this route the user must have the permission 'delete_group' or 'admin'.</p>
		<p><b>Note2</b>: The original groups can't be deleted, if you try will return an error.</p>
	"""
	return await service.delete({'id':id})



#_______________________________OTHERS_ROUTERS__________________________________#

#___________GRANT_PERMISSION___________#

#___GRANT__#

@router_grant_permission.post("/grant/permission/user", response_model=schemas.GrantResponseSchema)
async def grant_permission_to_user(data: schemas.GrantPermissionToUserSchema,
	service: AdminPermissionServiceInterface = Depends(get_grant_permission_service)):
	"""
		## Grant permission to User
		This route will grant permission to a user.
		<p><b>Note</b>: To use this route the user must have the permission 'grant_permission_to' or 'admin'.</p>
	"""
	return await service.grant_permission_to_user(data.dict())

@router_grant_permission.post("/grant/permission/group", response_model=schemas.GrantResponseSchema)
async def grant_permission_to_group(data: schemas.GrantPermissionToGroupSchema,
	service: AdminPermissionServiceInterface = Depends(get_grant_permission_service)):
	"""
		## Grant permission to Group
		This route will grant permission to a group.
		<p><b>Note</b>: To use this route the user must have the permission 'grant_permission_to' or 'admin'.</p>
	"""
	return await service.grant_permission_to_group(data.dict())

#__REMOVE__#

@router_grant_permission.delete("/grant/permission/user", response_model=schemas.RemoveResponseSchema)
async def remove_user_permission(data: schemas.RemoveUserPermissionSchema,
	service: AdminPermissionServiceInterface = Depends(get_remove_permission_service)):
	"""
		## Remove User Permission
		This route will remove permission from user.
		<p><b>Note</b>: To use this route the user must have the permission 'remove_permission_from' or 'admin'.</p>
	"""
	return await service.remove_user_permission(data.dict())

@router_grant_permission.delete("/grant/permission/group", response_model=schemas.RemoveResponseSchema)
async def remove_group_permission(data: schemas.RemoveGroupPermissionSchema,
	service: AdminPermissionServiceInterface = Depends(get_remove_permission_service)):
	"""
		## Remove Group Permission
		This route will remove permission from group.
		<p><b>Note</b>: To use this route the user must have the permission 'remove_permission_from' or 'admin'.</p>
		<p><b>Note</b>: The original group permission can't be removed. If you try will return an error.</p>
	"""
	return await service.remove_group_permission(data.dict())


#______________GRANT_GROUP______________#

#___GRANT__#

@router_grant_group.post("/grant/group/user", response_model=schemas.GrantResponseSchema)
async def add_user_to_group(data: schemas.AddUserToGroupSchema,
	service: AdminGroupServiceInterface = Depends(get_add_user_to_group_service)):
	"""
		## Add user to Group
		This route will add user to a group.
		<p><b>Note</b>: To use this route the user must have the permission 'add_user_to_group' or 'admin'.</p>
	"""
	return await service.add_user_to_group(data.dict())

#__REMOVE__#

@router_grant_group.delete("/grant/group/user", response_model=schemas.RemoveResponseSchema)
async def remove_user_from_group(data: schemas.RemoveUserFromGroupSchema,
	service: AdminGroupServiceInterface = Depends(get_remove_user_from_group_service)):
	"""
		## Remove user from Group
		This route will remove user from group.
		<p><b>Note</b>: To use this route the user must have the permission 'remove_user_from_group' or 'admin'.</p>
	"""
	return await service.remove_user_from_group(data.dict())


#_________________SESSION_MANAGEMENT__________________#

@router_session_mng.delete("/sessions", response_model=schemas.RemoveResponseSchema)
async def remove_session(data: schemas.RemoveSessionSchema,
	service: AdminSessionServiceInterface = Depends(get_delete_session_service)):
	"""
		## Remove Session
		This route will delete user sesssions.
		<p><b>Note</b>: To use this route the user must have the permission 'delete_session' or 'admin'.</p>
		<p><b>Note2</b>: The *session_id* is optional, when not setted all user sessions will be deleted.</p>
		<p><b>Note3</b>: When a session was deleted the session refresh token wan't work anymore, but the access token will work until expire.</p>
	"""
	return await service.remove_session(data.dict())