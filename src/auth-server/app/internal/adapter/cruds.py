from .database import (
    #Base postgres cruds
    AsyncPostgresCRUD, AsyncRelationalPostgresCRUD,
    #Postgres models
    UserTable, RandomTable, PermissionTable, GroupTable, UserPermissionTable,
    UserGroupTable, GroupPermissionTable, SessionTable, LogTable)
from sqlalchemy import and_
#Entities
from app.internal.domain.entities import (Random, User, Permission, Group, 
    UserPermission, UserGroup, GroupPermission, Log, Session)


#________________LOG__________________#
class LogCRUD(AsyncPostgresCRUD):
    model_class=LogTable
    entity_class=Log
    tablename= LogTable.__tablename__


#________________USER__________________#
class UserCRUD(AsyncPostgresCRUD):
    model_class=UserTable
    entity_class=User
    tablename= UserTable.__tablename__

    def _get_query(self, unique_data:dict):
        if 'email' in unique_data: 
            return self.model_class.email == unique_data['email']
        else: return self.model_class.id == unique_data['id']


#___________________Random________________#
class RandomCRUD(AsyncRelationalPostgresCRUD):
    model_class=RandomTable
    entity_class=Random
    tablename= RandomTable.__tablename__

    def _get_query(self, unique_data:dict):
        return and_(self.model_class.id==unique_data['id'], 
            self.model_class.flow==unique_data['flow'])

    def _get_query_by(self, repeated_data:dict):
        if 'id' in repeated_data: 
            return self.model_class.id==repeated_data['id']
        else: return self.model_class.flow==repeated_data['flow']


#_______________GROUP_______________#
class GroupCRUD(AsyncPostgresCRUD):
    model_class=GroupTable
    entity_class=Group
    tablename= GroupTable.__tablename__


#_________________Permission_______________#
class PermissionCRUD(AsyncPostgresCRUD):
    model_class=PermissionTable
    entity_class=Permission
    tablename=PermissionTable.__tablename__


#___________________Session____________________#
class SessionCRUD(AsyncRelationalPostgresCRUD):
    model_class=SessionTable
    entity_class=Session
    tablename=SessionTable.__tablename__

    def _get_query(self, unique_data:dict):
        return and_(self.model_class.user_id==unique_data['user_id'], 
            self.model_class.session_id==unique_data['session_id'])

    def _get_query_by(self, repeated_data:dict):
        if 'user_id' in repeated_data: 
            return self.model_class.user_id==repeated_data['user_id']
        else: return self.model_class.session_id==repeated_data['session_id']

#___________________UserPermission_______________#
class UserPermissionCRUD(AsyncRelationalPostgresCRUD):
    model_class=UserPermissionTable
    entity_class=UserPermission
    tablename=UserPermissionTable.__tablename__

    def _get_query(self, unique_data:dict):
        return and_(self.model_class.user_id==unique_data['user_id'], 
            self.model_class.permission_id==unique_data['permission_id'])

    def _get_query_by(self, repeated_data:dict):
        if 'user_id' in repeated_data: 
            return self.model_class.user_id==repeated_data['user_id']
        else: return self.model_class.permission_id==repeated_data['permission_id']


#___________________UserGroup_______________#
class UserGroupCRUD(AsyncRelationalPostgresCRUD):
    model_class=UserGroupTable
    entity_class=UserGroup
    tablename=UserGroupTable.__tablename__ 

    def _get_query(self, unique_data:dict):
        return and_(self.model_class.user_id==unique_data['user_id'], 
            self.model_class.group_id==unique_data['group_id'])

    def _get_query_by(self, repeated_data:dict):
        if 'user_id' in repeated_data: 
            return self.model_class.user_id==repeated_data['user_id']
        else: return self.model_class.group_id==repeated_data['group_id']


#___________________GroupPermission________________#
class GroupPermissionCRUD(AsyncRelationalPostgresCRUD):
    model_class=GroupPermissionTable
    entity_class=GroupPermission
    tablename= GroupPermissionTable.__tablename__

    def _get_query(self, unique_data:dict):
        return and_(self.model_class.group_id==unique_data['group_id'], 
            self.model_class.permission_id==unique_data['permission_id'])

    def _get_query_by(self, repeated_data:dict):
        if 'group_id' in repeated_data: 
            return self.model_class.group_id==repeated_data['group_id']
        else: return self.model_class.permission_id==repeated_data['permission_id']