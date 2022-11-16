import abc
import uuid
import asyncio
import json
from datetime import datetime

#interfaces
from app.internal.domain.interfaces import ManagerInterface, RandomManagerInterface, RelationalManagerInterface
from .interfaces import (AdminCRUDServiceInterface, AdminPermissionServiceInterface, AdminGroupServiceInterface,
    AdminSessionServiceInterface)
from app.internal.adapter.interfaces import EmailSenderInterface, TransactionProcessorInterface

#others
from app.internal.exceptions import HTTPExceptionGenerator, DictValidatorException
from app.internal import warnings as war
from app.internal.validators import (CreateUserAdminValidator, SetUserAdminValidator,
    GetUserAdminValidator, CreatePermissionAdminValidator, GetPermissionAdminValidator,
    CreateGroupAdminValidator, GetGroupAdminValidator, BaseDictValidator,
    GrantPermissionToUserValidator, GrantPermissionToGroupValidator, RemoveUserPermissionValidator,
    RemoveGroupPermissionValidator, AddUserToGroupValidator, RemoveUserFromGroupValidator,
    RemoveSessionValidator)



class BaseAdminService():

    def _remove_none_values(self, data:dict):
        #remove all keys with None values on dict 'data'
        for key, value in dict(data).items():
            if value is None: del data[key]
        return data
    
    def _validate_received_data(self, dict_validator_class, data: dict):

        try: dict_validator_class.validate(data)
        except Exception as ex:
            raise HTTPExceptionGenerator(status_code=400, detail=json.loads(ex.json()))

    def _check_not_found(self, object, name:str):
        """
        check if the object not exist and raise exception
        when the object is None it's mean that, the object not exist
        """
        if object is None:
            raise HTTPExceptionGenerator(status_code=404,
                detail=HTTPExceptionGenerator.generate_detail(fields=[name], 
                    error_type='not_found', msg=war.not_found_msg(name)))
        return object

    def _check_found(self, object, name:str):
        """
        check if the object exist and raise exception
        when the object is not None it's mean that, the object exist
        """
        if object is not None:
            raise HTTPExceptionGenerator(status_code=400,
                detail=HTTPExceptionGenerator.generate_detail(fields=[name], 
                    error_type='exist', msg=war.exist_msg(name)))
    
    def _validate_skip_limit(self, skip:int, limit:int):
        if skip<0 or limit<1:
            raise HTTPExceptionGenerator(status_code=400,
                detail=HTTPExceptionGenerator.generate_detail(fields=['skip','limit'], 
                    error_type='range', msg=war.incorrect_msg('range')))


    def _check_is_original(self, is_original:bool, name:str):
        if is_original:
            raise HTTPExceptionGenerator(status_code=403,
                detail=HTTPExceptionGenerator.generate_detail(fields=[name], 
                    error_type='original', msg=war.delete_error_msg(name)))


#____________________________________CRUD_SERVICES_________________________________________#


#________________________USER_CRUD_SERVICE_______________________________________#

class UserCRUDService(BaseAdminService, AdminCRUDServiceInterface):

    def __init__(self, user_id, transaction_processor: TransactionProcessorInterface,
        user_manager: ManagerInterface, random_manager: RandomManagerInterface,    
        user_permission_manager: RelationalManagerInterface, user_group_manager: RelationalManagerInterface,
        session_manager: RelationalManagerInterface, email_sender: EmailSenderInterface):

        self._transaction_processor = transaction_processor
        self._user_id = user_id
        self._user_manager = user_manager
        self._random_manager = random_manager
        self._user_permission_manager = user_permission_manager
        self._user_group_manager = user_group_manager
        self._session_manager = session_manager
        self._email_sender = email_sender

    
    async def create(self, data: dict):
        #data.keys() = ['email', 'username', 'password', 'is_complete']
        self._validate_received_data(CreateUserAdminValidator, data)
        
        #check if the email exist
        self._check_found(
            await self._user_manager.get({'email':data['email']}), 'email')
        
        transactions_list = []

        #create the user
        user, tran = self._user_manager.create(data)
        transactions_list.extend(tran)

        #check if the user have signup completed
        if user.is_complete:
            #process transactions
            await self._transaction_processor.process(transactions_list)
            return {'id':user.id}

        #create random
        random, tran = self._random_manager.create({'id':user.id, 'flow':'signup'})
        transactions_list.extend(tran)

        #send signup email
        self._email_sender.send_signup_email(user.email, random.key)

        #process transactions
        await self._transaction_processor.process(transactions_list)

        return {'id':user.id}

    async def get(self, data:dict):
        #data.keys() = ['id']
        self._validate_received_data(GetUserAdminValidator, data)

        #search user, user_permissions and user_group using user_id
        result = await asyncio.gather(*[self._user_manager.get(data),
            self._user_permission_manager.get_many_by({'user_id':data['id']}),
            self._user_group_manager.get_many_by({'user_id':data['id']}),
            self._session_manager.get_many_by({'user_id':data['id']})])
        
        #check if the user_id exist
        user =  self._check_not_found(result[0], 'id')
        permissions = []
        groups = []
        sessions = []

        for user_permission in result[1]:
            permissions.append(user_permission.permission_id)
        
        for user_group in result[2]:
            groups.append(user_group.group_id)

        for session in result[3]:
            sessions.append({'id':session.session_id, 
                'expirated':session.expirated, 'created':session.created})
        
        user.permissions = permissions
        user.groups = groups
        user.sessions = sessions

        return user

    async def get_many(self, skip:int, limit:int):
        self._validate_skip_limit(skip, limit)
        return await self._user_manager.get_many(skip,limit)

    async def set(self, data:dict):
        #data.keys() = ['id','username'] or ['id','is_complete']
        data = self._remove_none_values(data)
        self._validate_received_data(SetUserAdminValidator, data)
        
        #check if the user exist
        user = self._check_not_found(
            await self._user_manager.get({'id':data['id']}), 'id')
        del data['id']
        
        transactions_list = []

        #set the user
        tran = self._user_manager.update({'id':user.id}, data)
        transactions_list.extend(tran)

        #check is_complete to delete random
        if 'is_complete' in data:
            if not user.is_complete and data['is_complete']:
                tran = self._random_manager.delete({'id':user.id, 'flow':'signup'})
                transactions_list.extend(tran)

        #process transactions
        await self._transaction_processor.process(transactions_list)

        return {'detail':'user setted'}
    
    async def delete(self, data:dict):
        #data.keys() = ['id']
        self._validate_received_data(GetUserAdminValidator, data)

        #check if the user exist
        user = self._check_not_found(
            await self._user_manager.get(data), 'id')

        transactions_list = []

        #delete all user_permissions
        tran = self._user_permission_manager.delete_many_by({'user_id':user.id})
        transactions_list.extend(tran)

        #delete all user_groups
        tran = self._user_group_manager.delete_many_by({'user_id':user.id})
        transactions_list.extend(tran)

        #delete all sessions
        tran = self._session_manager.delete_many_by({'user_id':user.id})
        transactions_list.extend(tran)

        #delete all randoms
        tran = self._random_manager.delete_many_by({'id':user.id})
        transactions_list.extend(tran)

        #delete user
        tran = self._user_manager.delete(data)
        transactions_list.extend(tran)

        #process transactions
        await self._transaction_processor.process(transactions_list)

        return {'detail':'user deleted'}



#________________________PERMISSION_CRUD_SERVICE_______________________________________#

class PermissionCRUDService(BaseAdminService, AdminCRUDServiceInterface):

    def __init__(self, user_id, transaction_processor: TransactionProcessorInterface, 
        permission_manager: ManagerInterface, user_permission_manager: RelationalManagerInterface,
        group_permission_manager: RelationalManagerInterface):

        self._transaction_processor = transaction_processor
        self._user_id = user_id
        self._permission_manager = permission_manager
        self._user_permission_manager = user_permission_manager
        self._group_permission_manager = group_permission_manager
    
    async def create(self, data: dict):
        #data.keys() = ['id']
        self._validate_received_data(CreatePermissionAdminValidator, data)
        
        #check if the id exist
        self._check_found(
            await self._permission_manager.get({'id':data['id']}), 'id')
        
        #create permission
        permission, tran = self._permission_manager.create(data)

        #process transactions
        await self._transaction_processor.process(tran)

        return {'id':permission.id}

    async def get(self, data:dict):
        #data.keys() = ['id']
        self._validate_received_data(GetPermissionAdminValidator, data)

        #search permission and group_permission using permission_id
        result = await asyncio.gather(*[self._permission_manager.get(data),
            self._group_permission_manager.get_many_by({'permission_id':data['id']})])
        
        #check if the permission exist
        permission=self._check_not_found(result[0], 'id')
        groups = []

        for group_permission in result[1]:
            groups.append(group_permission.group_id)    
        permission.groups = groups

        return permission
    
    async def get_many(self, skip:int, limit:int):
        self._validate_skip_limit(skip, limit)
        return await self._permission_manager.get_many(skip,limit)

    def set(self, data:dict):
        pass
    
    async def delete(self, data:dict):
        #data.keys() = ['id']
        self._validate_received_data(GetPermissionAdminValidator, data)

        permission = self._check_not_found(await self._permission_manager.get(data), 'id')
        
        #check if the permission is not original
        self._check_is_original(permission.is_original, 'permission')

        transactions_list = []

        #delete all user_permissions
        tran = self._user_permission_manager.delete_many_by({'permission_id':permission.id})
        transactions_list.extend(tran)

        #delete all group_permissions
        tran = self._group_permission_manager.delete_many_by({'permission_id':permission.id})
        transactions_list.extend(tran)

        #delete permission
        tran = self._permission_manager.delete(data)
        transactions_list.extend(tran)

        #process transactions
        await self._transaction_processor.process(transactions_list)

        return {'detail':'permission deleted'}



#________________________GROUP_CRUD_SERVICE_______________________________________#

class GroupCRUDService(BaseAdminService, AdminCRUDServiceInterface):

    def __init__(self, user_id, transaction_processor: TransactionProcessorInterface,
        group_manager: ManagerInterface, user_group_manager: RelationalManagerInterface,
        group_permission_manager: RelationalManagerInterface):
        
        self._transaction_processor = transaction_processor
        self._user_id = user_id
        self._group_manager = group_manager
        self._user_group_manager = user_group_manager
        self._group_permission_manager = group_permission_manager
    
    async def create(self, data: dict):
        #data.keys() = ['id']
        self._validate_received_data(CreateGroupAdminValidator, data)
        
        #check if the id exist
        self._check_found(await self._group_manager.get(data), 'id')
        
        #create group
        group, tran = self._group_manager.create(data)
        
        #process transactions
        await self._transaction_processor.process(tran)
        
        return {'id':group.id}

    async def get(self, data:dict):
        #data.keys() = ['id']
        self._validate_received_data(GetGroupAdminValidator, data)

        #search group and group_permission using group_id
        result = await asyncio.gather(*[self._group_manager.get(data),
            self._group_permission_manager.get_many_by({'group_id':data['id']})])
        
        #check if the group exist
        group=self._check_not_found(result[0], 'id')
        permissions=[]

        for group_permission in result[1]:
            permissions.append(group_permission.permission_id)
        group.permissions = permissions

        return group
    
    async def get_many(self, skip:int, limit:int):
        self._validate_skip_limit(skip, limit)
        return await self._group_manager.get_many(skip,limit)

    def set(self, data:dict):
        pass
    
    async def delete(self, data:dict):
        #data.keys() = ['id']
        self._validate_received_data(GetGroupAdminValidator, data)

        group = self._check_not_found(await self._group_manager.get(data), 'id')

        #check if the group is not original
        self._check_is_original(group.is_original, 'group')

        transactions_list = []

        #delete all user_groups
        tran = self._user_group_manager.delete_many_by({'group_id':group.id})
        transactions_list.extend(tran)

        #delete all group_permissions
        tran=self._group_permission_manager.delete_many_by({'group_id':group.id})
        transactions_list.extend(tran)

        #delete group
        tran = self._group_manager.delete(data)
        transactions_list.extend(tran)

        #process transactions
        await self._transaction_processor.process(transactions_list)

        return {'detail':'group deleted'}



#____________________________________OTHERS_SERVICES_________________________________________#

#_______________________PERMISSION_GRANT_SERVICE____________________________________#

class PermissionGrantService(BaseAdminService, AdminPermissionServiceInterface):

    def __init__(self, user_id, transaction_processor: TransactionProcessorInterface,
        permission_manager: ManagerInterface, group_manager: ManagerInterface,
        user_manager: ManagerInterface, user_permission_manager: RelationalManagerInterface,
        group_permission_manager: RelationalManagerInterface):

        self._transaction_processor = transaction_processor
        self._user_id = user_id
        self._permission_manager = permission_manager
        self._group_manager = group_manager
        self._user_manager = user_manager
        self._user_permission_manager = user_permission_manager
        self._group_permission_manager = group_permission_manager
    
    async def _search_user_permission(self, data:dict):
        #search user, permission and user_permission
        result = await asyncio.gather(*[self._user_manager.get({'id':data['user_id']}),
            self._permission_manager.get({'id':data['permission_id']}),
            self._user_permission_manager.get(data)])

        #check if the user exist
        user = self._check_not_found(result[0], 'user_id')
        #check if the permission exist 
        permission = self._check_not_found(result[1], 'permission_id')

        return result
    
    async def _search_group_permission(self, data:dict):
        #search group, permission and group_permission
        result = await asyncio.gather(*[self._group_manager.get({'id':data['group_id']}),
            self._permission_manager.get({'id':data['permission_id']}),
            self._group_permission_manager.get(data)])

        #check if the group exist
        group = self._check_not_found(result[0], 'group_id')
        #check if the permission exist 
        permission = self._check_not_found(result[1], 'permission_id')

        return result

    async def grant_permission_to_user(self, data: dict):
        #data.keys() = ['user_id', 'permission_id']
        self._validate_received_data(GrantPermissionToUserValidator, data)

        #search user, permission, user_permission and check if the user and permission exist
        result = await self._search_user_permission(data)

        #check if the user_permission not exist
        self._check_found(result[2], 'user_permission')

        #create user_permission
        user_permission, tran = self._user_permission_manager.create(data)

        #process transactions
        await self._transaction_processor.process(tran)

        return {'detail':'permission granted'}

    async def grant_permission_to_group(self, data: dict):
        #data.keys() = ['group_id', 'permission_id']
        self._validate_received_data(GrantPermissionToGroupValidator, data)

        #search group, permission, group_permission and check if the group and permission exist
        result = await self._search_group_permission(data)

        #check if the group_permission not exist
        self._check_found(result[2], 'group_permission')

        #create group_permission
        group_permission, tran =self._group_permission_manager.create(data)
        
        #process transactions
        await self._transaction_processor.process(tran)

        return {'detail':'permission granted'}

    async def remove_user_permission(self, data: dict):
        #data.keys() = ['user_id', 'permission_id']
        self._validate_received_data(RemoveUserPermissionValidator, data)

        #search user, permission, user_permission and check if the user and permission exist
        result = await self._search_user_permission(data)

        #check if the user_permission exist
        user_permission = self._check_not_found(result[2], 'user_permission')

        #delete user_permission
        tran = self._user_permission_manager.delete(data)

        #process transactions
        await self._transaction_processor.process(tran)

        return {'detail':'permission removed'}

    async def remove_group_permission(self, data: dict):
        #data.keys() = ['group_id', 'permission_id']
        self._validate_received_data(RemoveGroupPermissionValidator, data)

        #search group, permission, group_permission and check if the group and permission exist
        result = await self._search_group_permission(data)

        #check if the group_permission exist
        group_permission = self._check_not_found(result[2], 'group_permission')
        
        #check if the group_permission is not original
        self._check_is_original(group_permission.is_original, 'group_permission')

        #create group_permission
        tran = self._group_permission_manager.delete(data)

        #process transactions
        await self._transaction_processor.process(tran)

        return {'detail':'permission removed'}


#________________________GROUP_GRANT_SERVICE______________________________________#

class GroupGrantService(BaseAdminService, AdminGroupServiceInterface):

    def __init__(self, user_id, transaction_processor: TransactionProcessorInterface,
        group_manager: ManagerInterface, user_manager: ManagerInterface,
        user_group_manager: RelationalManagerInterface):

        self._transaction_processor = transaction_processor
        self._user_id = user_id
        self._group_manager = group_manager
        self._user_manager = user_manager
        self._user_group_manager = user_group_manager

    async def _search_user_group(self, data:dict):
        #search user, group and user_group
        result = await asyncio.gather(*[self._user_manager.get({'id':data['user_id']}),
            self._group_manager.get({'id':data['group_id']}),
            self._user_group_manager.get(data)])
        
        #check if the user exist
        user = self._check_not_found(result[0], 'user_id')
        #check if the group exist 
        group = self._check_not_found(result[1], 'group_id')
        
        return result
    
    async def add_user_to_group(self, data: dict):
        #data.keys() = ['user_id', 'group_id']
        self._validate_received_data(AddUserToGroupValidator, data)
        
        #search user, group, group_permission and check if the user and group exist
        result = await self._search_user_group(data)

        #check if the user_group not exist
        self._check_found(result[2], 'user_group')

        #create user_group
        user_group, tran = self._user_group_manager.create(data)

        #process transactions
        await self._transaction_processor.process(tran)

        return {'detail':'user added to group'}

    async def remove_user_from_group(self, data: dict):
        #data.keys() = ['user_id', 'group_id']
        self._validate_received_data(RemoveUserFromGroupValidator, data)
        
        #search user, group, group_permission and check if the user and group exist
        result = await self._search_user_group(data)

        #check if the user_group not exist
        user_group = self._check_not_found(result[2], 'user_group')

        #delete user_group
        tran = self._user_group_manager.delete(data)

        #process transactions
        await self._transaction_processor.process(tran)

        return {'detail':'user removed from group'}



#____________________SESSION_MANAGEMENT_SERVICE______________________________________#

class SessionManagementService(BaseAdminService, AdminSessionServiceInterface):

    def __init__(self, user_id, transaction_processor: TransactionProcessorInterface,
        user_manager: ManagerInterface, session_manager: RelationalManagerInterface):

        self._transaction_processor = transaction_processor
        self._user_id = user_id
        self._user_manager = user_manager
        self._session_manager = session_manager

    async def _remove_one_session(self, data:dict):
        result = await asyncio.gather(*[self._user_manager.get({'id':data['user_id']}),
            self._session_manager.get({'user_id':data['user_id'], 'session_id':data['session_id']})])

        #check if the user exist
        user = self._check_not_found(result[0], 'user_id')
        #check if the session exist 
        session = self._check_not_found(result[1], 'session')
        
        #delete
        return self._session_manager.delete({'user_id':data['user_id'], 'session_id':data['session_id']})
    
    async def _remove_many_sessions(self, data:dict):
        #check if the user exist
        user = self._check_not_found( 
            await self._user_manager.get({'id':data['user_id']}),'user_id')
        
        #delete all sessions
        return self._session_manager.delete_many_by({'user_id':user.id})
        
    async def remove_session(self, data: dict):
        #data.keys() = ['user_id'] or ['user_id', 'session_id']
        data = self._remove_none_values(data)
        self._validate_received_data(RemoveSessionValidator, data)
        
        tran=None
        #check user and session
        if 'session_id' in data: tran = await self._remove_one_session(data)
        else: tran = await self._remove_many_sessions(data)

        #process transactions
        await self._transaction_processor.process(tran)
        
        return {'detail':'Session removed'}