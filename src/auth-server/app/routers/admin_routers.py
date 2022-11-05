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


router = APIRouter()

#_________________________________CRUD_ROUTERS_______________________________#

#______________USERS______________#

#___CREATE___#

@router.post("/users", response_model=schemas.CreateUserResponseSchema, status_code=201)
async def create_user(data: schemas.CreateUserSchema, service: AdminCRUDServiceInterface = Depends(get_create_user_service)):
	return await service.create(data.dict())

#_____GET_____#

@router.get("/users", response_model=List[schemas.UserSchema])
async def get_users(skip:int=0, limit:int=100, service: AdminCRUDServiceInterface = Depends(get_read_user_service)):
	return await service.get_many(skip,limit)

@router.get("/users/{id}", response_model=schemas.UserSpecificSchema)
async def get_user(id: uuid.UUID, service: AdminCRUDServiceInterface = Depends(get_read_user_service)):
	return await service.get({'id':id})

#_____UPDATE___#

@router.put("/users/{id}", response_model=schemas.SetUserResponseSchema)
async def set_user(data: schemas.SetUserSchema, id: uuid.UUID, 
	service: AdminCRUDServiceInterface = Depends(get_update_user_service)):
	data_dict = data.dict()
	data_dict['id'] = id
	return await service.set(data_dict)

#____DELETE____#

@router.delete("/users/{id}", response_model=schemas.DeleteUserResponseSchema)
async def delete_user(id: uuid.UUID, service: AdminCRUDServiceInterface = Depends(get_delete_user_service)):
	return await service.delete({'id':id})


#______________PERMISSION______________#

#___CREATE___#

@router.post("/permissions", response_model=schemas.CreatePermissionResponseSchema, status_code=201)
async def create_permission(data: schemas.CreatePermissionSchema, service: AdminCRUDServiceInterface = Depends(get_create_permission_service)):
	return await service.create(data.dict())

#_____GET_____#

@router.get("/permissions", response_model=List[schemas.PermissionSchema])
async def get_permissions(skip:int=0, limit:int=100, service: AdminCRUDServiceInterface = Depends(get_read_permission_service)):
	return await service.get_many(skip,limit)

@router.get("/permissions/{id}", response_model=schemas.PermissionSpecificSchema)
async def get_permission(id: str, service: AdminCRUDServiceInterface = Depends(get_read_permission_service)):
	return await service.get({'id':id})

#____DELETE____#

@router.delete("/permissions/{id}", response_model=schemas.DeletePermissionResponseSchema)
async def delete_permission(id: str, service: AdminCRUDServiceInterface = Depends(get_delete_permission_service)):
	return await service.delete({'id':id})


#_________________GROUP_________________#

#___CREATE___#

@router.post("/groups", response_model=schemas.CreateGroupResponseSchema, status_code=201)
async def create_group(data: schemas.CreateGroupSchema, service: AdminCRUDServiceInterface = Depends(get_create_group_service)):
	return await service.create(data.dict())

#_____GET_____#

@router.get("/groups", response_model=List[schemas.GroupSchema])
async def get_groups(skip:int=0, limit:int=100, service: AdminCRUDServiceInterface = Depends(get_read_group_service)):
	return await service.get_many(skip,limit)

@router.get("/groups/{id}", response_model=schemas.GroupSpecificSchema)
async def get_group(id: str, service: AdminCRUDServiceInterface = Depends(get_read_group_service)):
	return await service.get({'id':id})

#____DELETE____#

@router.delete("/groups/{id}", response_model=schemas.DeleteGroupResponseSchema)
async def delete_group(id: str, service: AdminCRUDServiceInterface = Depends(get_delete_group_service)):
	return await service.delete({'id':id})



#_______________________________OTHERS_ROUTERS__________________________________#

#___________GRANT_PERMISSION___________#

#___GRANT__#

@router.post("/grant/permission/user", response_model=schemas.GrantResponseSchema)
async def grant_permission_to_user(data: schemas.GrantPermissionToUserSchema,
	service: AdminPermissionServiceInterface = Depends(get_grant_permission_service)):
	return await service.grant_permission_to_user(data.dict())

@router.post("/grant/permission/group", response_model=schemas.GrantResponseSchema)
async def grant_permission_to_group(data: schemas.GrantPermissionToGroupSchema,
	service: AdminPermissionServiceInterface = Depends(get_grant_permission_service)):
	return await service.grant_permission_to_group(data.dict())

#__REMOVE__#

@router.delete("/grant/permission/user", response_model=schemas.RemoveResponseSchema)
async def remove_user_permission(data: schemas.RemoveUserPermissionSchema,
	service: AdminPermissionServiceInterface = Depends(get_remove_permission_service)):
	return await service.remove_user_permission(data.dict())

@router.delete("/grant/permission/group", response_model=schemas.RemoveResponseSchema)
async def remove_group_permission(data: schemas.RemoveGroupPermissionSchema,
	service: AdminPermissionServiceInterface = Depends(get_remove_permission_service)):
	return await service.remove_group_permission(data.dict())


#______________GRANT_GROUP______________#

#___GRANT__#

@router.post("/grant/group/user", response_model=schemas.GrantResponseSchema)
async def add_user_to_group(data: schemas.AddUserToGroupSchema,
	service: AdminGroupServiceInterface = Depends(get_add_user_to_group_service)):
	return await service.add_user_to_group(data.dict())

#__REMOVE__#

@router.delete("/grant/group/user", response_model=schemas.RemoveResponseSchema)
async def remove_user_from_group(data: schemas.RemoveUserFromGroupSchema,
	service: AdminGroupServiceInterface = Depends(get_remove_user_from_group_service)):
	return await service.remove_user_from_group(data.dict())


#_________________SESSION_MANAGEMENT__________________#

@router.delete("/sessions", response_model=schemas.RemoveResponseSchema)
async def remove_session(data: schemas.RemoveSessionSchema,
	service: AdminSessionServiceInterface = Depends(get_delete_session_service)):
	return await service.remove_session(data.dict())