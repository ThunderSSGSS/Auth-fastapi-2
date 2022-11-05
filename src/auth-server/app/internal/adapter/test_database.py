import json
import os
import uuid
from datetime import datetime

"""
Database equema
{
    'tablename': [{}, {}, {}, ...],
    'tablename2': [{}, {}, {}, ...],
    ...
}
"""

__adim_user_id= uuid.uuid4()
__date = datetime.now()
_database={
    'permissions': [
        #admins permissions
        {'id':'admin','created':__date, 'updated':__date, 'is_original':True},
        
        {'id':'create_user', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'read_user', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'update_user', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'delete_user', 'created':__date, 'updated':__date, 'is_original':True},
        
        {'id':'create_permission', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'read_permission', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'delete_permission', 'created':__date, 'updated':__date, 'is_original':True},
        
        {'id':'create_group', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'read_group', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'delete_group', 'created':__date, 'updated':__date, 'is_original':True},
        
        {'id':'grant_permission_to', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'remove_permission_from', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'add_user_to_group', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'remove_user_from_group', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'delete_session', 'created':__date, 'updated':__date, 'is_original':True},

        #normal permissions
        {'id':'logout', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'set_own_password', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'set_own_username', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'set_own_email', 'created':__date, 'updated':__date, 'is_original':True},
        {'id':'read_own_user_data', 'created':__date, 'updated':__date, 'is_original':True}        
    ],

    'groups':[
        {'id':'normal', 'created':__date, 'updated':__date, 'is_original':True}
    ],

    'group_permissions':[
        {'group_id':'normal', 'permission_id':'logout', 'created':__date, 'updated':__date, 'is_original':True},
        {'group_id':'normal', 'permission_id':'set_own_password', 'created':__date, 'updated':__date, 'is_original':True},
        {'group_id':'normal', 'permission_id':'set_own_email', 'created':__date, 'updated':__date, 'is_original':True},
        {'group_id':'normal', 'permission_id':'set_own_username', 'created':__date, 'updated':__date, 'is_original':True},
        {'group_id':'normal', 'permission_id':'read_own_user_data', 'created':__date, 'updated':__date, 'is_original':True}
    ],

    'users': [
        {'id':__adim_user_id, 'email':'admin@admin.com', 'username':'ADMIN', 'password':'naa', 
            'is_complete':True,'created':__date, 'updated':__date}
    ],

    'user_permissions': [
        {'user_id':__adim_user_id, 'permission_id':'admin', 'created':__date, 'updated':__date}
    ]
}


def _compare(inserted:dict, db_data:dict):
    value_db=None
    for atr, value in inserted.items():
        value_db = db_data.get(atr)
        if str(value) != str(value_db): return False
    return True

#___________METHODS__________________________________________#

def test_find(tablename:str, unique_data:dict):
    list_data = _database.get(tablename)
    if list_data is None: return None
    for data in list_data:
        if _compare(unique_data, data): return data
    return None

def test_find_many(tablename:str, skip:int=0, limit:int=100):
    list_data = _database.get(tablename)
    if list_data is None: return []
    if len(list_data)>limit: return list_data[skip:limit]
    else: return list_data

def test_find_many_by(tablename:str, repeated_data:dict):
    list_data = _database.get(tablename)
    list_return_data=[]
    if list_data is None: return list_return_data
    for data in list_data:
        if _compare(repeated_data, data):
            list_return_data.append(data)
    return list_return_data

def test_save(tablename:str, data:dict):
    list_data = _database.get(tablename)
    if list_data is None: _database[tablename] = [data]
    else: 
        list_data.append(data)
        _database[tablename] = list_data

def test_update(tablename:str, unique_data:dict, new_data:dict):
    list_data = _database.get(tablename)
    if list_data is not None:
        for posi in range(len(list_data)):
            if _compare(unique_data, list_data[posi]):
                data = list_data[posi]
                for atr, value in new_data.items():
                    data[atr] = value
                list_data[posi] = data
                break
    _database[tablename] = list_data

def test_delete(tablename:str, unique_data:dict):
    list_data = _database.get(tablename)
    if list_data is not None:
        for posi in range(len(list_data)):
            if _compare(unique_data, list_data[posi]):
                del list_data[posi]
                break
    _database[tablename] = list_data

def test_delete_many_by(tablename:str, repeated_data:dict):
    list_data = _database.get(tablename)
    list_posi = []
    deleted_count = 0
    if list_data is not None:
        for posi in range(len(list_data)):
            if _compare(repeated_data, list_data[posi]):
                list_posi.append(posi)
        for posi in list_posi:
            del list_data[posi-deleted_count]
            deleted_count+=1
    _database[tablename] = list_data