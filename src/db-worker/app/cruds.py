from app.database import (
    #Base postgres cruds
    BaseEDIT, BaseRelationalEDIT,
    #Postgres models
    UserTable, RandomTable, PermissionTable, GroupTable, UserPermissionTable,
    UserGroupTable, GroupPermissionTable, SessionTable, LogTable)
from sqlalchemy import and_
#validators
from app.validators import (CreateUserValidator, UpdateUserValidator, 
    CreateRandomValidator, UpdateRandomValidator, CreatePermissionValidator,
    UpdatePermissionValidator, CreateGroupValidator, UpdateGroupValidator,
    CreateUserPermissionValidator, CreateUserGroupValidator, 
    CreateGroupPermissionValidator, CreateLogValidator, CreateSessionValidator)



#________LOG_____________#
class LogEDIT(BaseEDIT):
    model_class=LogTable
    validator_create_class=CreateLogValidator

#_________USER_______________#
class UserEDIT(BaseEDIT):
    model_class=UserTable
    validator_create_class=CreateUserValidator
    validator_update_class=UpdateUserValidator

#________RANDOM_______________#
class RandomEDIT(BaseRelationalEDIT):
    model_class=RandomTable
    validator_create_class=CreateRandomValidator
    validator_update_class=UpdateRandomValidator

    def _get_query(self, unique_data_dict:dict):
        return and_(self.model_class.id==unique_data_dict['id'], 
            self.model_class.flow==unique_data_dict['flow'])
    
    def _get_query_by(self, repeated_data_dict:dict):
        if 'id' in repeated_data_dict: 
            return self.model_class.id==repeated_data_dict['id']
        else: return self.model_class.flow==repeated_data_dict['flow']


#_________GROUP_____________#
class GroupEDIT(BaseEDIT):
    model_class=GroupTable
    validator_create_class=CreateGroupValidator
    validator_update_class=UpdateGroupValidator

#________PERMISSION___________#
class PermissionEDIT(BaseEDIT):
    model_class=PermissionTable
    validator_create_class=CreatePermissionValidator
    validator_update_class=UpdatePermissionValidator

#____________SESSION_________________#
class SessionEDIT(BaseRelationalEDIT):
    model_class=SessionTable
    validator_create_class=CreateSessionValidator

    def _get_query(self, unique_data_dict:dict):
        return and_(self.model_class.user_id==unique_data_dict['user_id'], 
            self.model_class.session_id==unique_data_dict['session_id'])
    
    def _get_query_by(self, repeated_data_dict:dict):
        if 'user_id' in repeated_data_dict: 
            return self.model_class.user_id==repeated_data_dict['user_id']
        else: return self.model_class.session_id==repeated_data_dict['session_id']

#________USER_PERMISSION_____________#
class UserPermissionEDIT(BaseRelationalEDIT):
    model_class=UserPermissionTable
    validator_create_class=CreateUserPermissionValidator

    def _get_query(self, unique_data_dict:dict):
        return and_(self.model_class.user_id==unique_data_dict['user_id'], 
            self.model_class.permission_id==unique_data_dict['permission_id'])
    
    def _get_query_by(self, repeated_data_dict:dict):
        if 'user_id' in repeated_data_dict: 
            return self.model_class.user_id==repeated_data_dict['user_id']
        else: return self.model_class.permission_id==repeated_data_dict['permission_id']

#________USER_GROUPS___________________#
class UserGroupEDIT(BaseRelationalEDIT):
    model_class=UserGroupTable
    validator_create_class=CreateUserGroupValidator

    def _get_query(self, unique_data_dict:dict):
        return and_(self.model_class.user_id==unique_data_dict['user_id'], 
            self.model_class.group_id==unique_data_dict['group_id'])
    
    def _get_query_by(self, repeated_data_dict:dict):
        if 'user_id' in repeated_data_dict: 
            return self.model_class.user_id==repeated_data_dict['user_id']
        else: return self.model_class.group_id==repeated_data_dict['group_id']

#_________GROUP_PERMISSION___________________#
class GroupPermissionEDIT(BaseRelationalEDIT):
    model_class=GroupPermissionTable
    validator_create_class=CreateGroupPermissionValidator

    def _get_query(self, unique_data_dict:dict):
        return and_(self.model_class.group_id==unique_data_dict['group_id'], 
            self.model_class.permission_id==unique_data_dict['permission_id'])
    
    def _get_query_by(self, repeated_data_dict:dict):
        if 'group_id' in repeated_data_dict: 
            return self.model_class.group_id==repeated_data_dict['group_id']
        else: return self.model_class.permission_id==repeated_data_dict['permission_id']