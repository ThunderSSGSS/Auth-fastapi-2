from fastapi.testclient import TestClient
from typing import List
import uuid
import time

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from app.main import app

#Test components
from tests.test_auth_routers import AuthRouter, _random, ErrorValidator, ErrorCheck


client = TestClient(app)

_admin_email='admin@admin.com'
_admin_password='admin1234'

_user_email='example_created@gmail.com'
_user_password='example1234'
_user_username='example_user'

_permission1='change_nothing'
_permission2='change_nothing2'
_group='nothing'


#_____________ADMIN_ROUTERS___________________________________#

class AdminRouter():
    def __init__(self, access_token:str, client:TestClient=client):
        self.access_token = access_token
        self._client = client
    
    #_________USER_CRUD___________#

    def create_user(self, email:str, username:str, password:str, is_complete:bool):
        return self._client.post('/admin/users', json={'email':email, 'username':username,
            'password':password, 'is_complete':is_complete}, headers = {'Authorization':'Bearer '+self.access_token})
    
    def get_users(self):
        return self._client.get('/admin/users', headers = {'Authorization':'Bearer '+self.access_token})
    
    def get_user(self, id:str):
        return self._client.get('/admin/users/'+id, headers = {'Authorization':'Bearer '+self.access_token})
    
    def set_user(self, id:str, username:str, is_complete:bool):
        return self._client.put('/admin/users/'+id, json={'username':username, 'is_complete':is_complete},
            headers = {'Authorization':'Bearer '+self.access_token})
    
    def delete_user(self, id:str):
        return self._client.delete('/admin/users/'+id, headers = {'Authorization':'Bearer '+self.access_token})

    #_________PERMISSION_CRUD____________#

    def create_permission(self, id:str):
        return self._client.post('/admin/permissions', json={'id':id}, 
            headers = {'Authorization':'Bearer '+self.access_token})
    
    def get_permissions(self):
        return self._client.get('/admin/permissions', headers = {'Authorization':'Bearer '+self.access_token})
    
    def get_permission(self, id:str):
        return self._client.get('/admin/permissions/'+id, headers = {'Authorization':'Bearer '+self.access_token})
    
    def delete_permission(self, id:str):
        return self._client.delete('/admin/permissions/'+id, headers = {'Authorization':'Bearer '+self.access_token})
    
    #_________GROUP_CRUD________________#

    def create_group(self, id:str):
        return self._client.post('/admin/groups', json={'id':id}, 
            headers = {'Authorization':'Bearer '+self.access_token})
    
    def get_groups(self):
        return self._client.get('/admin/groups', headers = {'Authorization':'Bearer '+self.access_token})
    
    def get_group(self, id:str):
        return self._client.get('/admin/groups/'+id, headers = {'Authorization':'Bearer '+self.access_token})
    
    def delete_group(self, id:str):
        return self._client.delete('/admin/groups/'+id, headers = {'Authorization':'Bearer '+self.access_token})

    #_________GRANT_PERMISSIONS__________________#

    def grant_permission_to_user(self, user_id:str, permission_id:str):
        return self._client.post('/admin/grant/permission/user', 
            json={'user_id':user_id, 'permission_id':permission_id}, 
            headers = {'Authorization':'Bearer '+self.access_token})
    
    def grant_permission_to_group(self, group_id:str, permission_id:str):
        return self._client.post('/admin/grant/permission/group', 
            json={'group_id':group_id, 'permission_id':permission_id}, 
            headers = {'Authorization':'Bearer '+self.access_token})
    
    def remove_permission_from_user(self, user_id:str, permission_id:str):
        return self._client.delete('/admin/grant/permission/user', 
            json={'user_id':user_id, 'permission_id':permission_id}, 
            headers = {'Authorization':'Bearer '+self.access_token})
    
    def remove_permission_from_group(self, group_id:str, permission_id:str):
        return self._client.delete('/admin/grant/permission/group', 
            json={'group_id':group_id, 'permission_id':permission_id}, 
            headers = {'Authorization':'Bearer '+self.access_token})
    
    #_________GRANT_GROUP__________________#

    def add_user_to_group(self, user_id:str, group_id:str):
        return self._client.post('/admin/grant/group/user',
            json={'group_id':group_id, 'user_id':user_id}, 
            headers = {'Authorization':'Bearer '+self.access_token})
    
    def remove_user_from_group(self, user_id:str, group_id:str):
        return self._client.delete('/admin/grant/group/user',
            json={'group_id':group_id, 'user_id':user_id}, 
            headers = {'Authorization':'Bearer '+self.access_token})
    
    #_______SESSION_MANAGEMNT___________________#

    def remove_session(self, user_id:str, session_id:str):
        data = {'user_id':user_id, 'session_id':session_id}
        if session_id is None: data = {'user_id':user_id}
        return self._client.delete('/admin/sessions', json=data, 
            headers = {'Authorization':'Bearer '+self.access_token})




#_________________TESTS_ADMIN_USER_ROUTERS________________________________________#

router = AuthRouter(client)
admin_router = AdminRouter('s')


#____PREPARING_THE_ADMIN___________________________#

def test_forget_password_flow():
    #forget password
    response = router.forget_password(_admin_email)
    print(response.json())
    assert response.status_code==200
    
    #restaure password
    response = router.restaure_password(_admin_email, _admin_password, _random)
    print(response.json())
    assert response.status_code==200


def login():
    #authenticate
    response = router.authenticate(_admin_email, _admin_password)
    print(response.json())
    assert response.status_code==200
    admin_router.access_token = response.json()['access_token']
    return response

def logout():
    #logout
    response = router.logout(admin_router.access_token)
    print(response.json())
    assert response.status_code==200



#____SAME_FUNCTIONS_________________#

def _test_get_user(user_id:str):
    #get user informations
    response = admin_router.get_user(user_id)
    print(response.json())
    assert response.status_code==200

    #try to get user informations (not exist user)
    response = admin_router.get_user(str(uuid.uuid4()))
    print(response.json())
    assert response.status_code==404

    #get users
    response = admin_router.get_users()
    print(response.json())
    assert response.status_code==200

#______________________USER_CRUD_TEST_________________________#

def test_create_user_completed():
    #login admin
    response = login()

    #create user (with completed signup)
    response = admin_router.create_user(_user_email, _user_username, _user_password, True)
    print(response.json())
    assert response.status_code==201
    user_id = response.json()['id']

    #test get specific user
    _test_get_user(user_id)

    #authenticate with created user
    response = router.authenticate(_user_email, _user_password)
    print(response.json())
    assert response.status_code==200
    access_token = response.json()['access_token']

    #try logout with created user, but without logout permission
    response = router.logout(access_token)
    print(response.json())
    assert response.status_code==401
    assert ErrorCheck.check_locs(['access_token'], response.json())

    #Delete created user
    response = admin_router.delete_user(user_id)
    print(response.json())
    assert response.status_code==200

    #logout admin
    logout()


def test_create_user_not_completed():
    #login admin
    response = login()

    #create user (with no complete signup)
    response = admin_router.create_user(_user_email, _user_username, _user_password, False)
    print(response.json())
    assert response.status_code==201
    user_id = response.json()['id']

    #try to authenticate with created user (with no complete signup)
    response = router.authenticate(_user_email, _user_password)
    print(response.json())
    assert response.status_code==400
    assert ErrorCheck.check_locs(['signup'], response.json())

    #Delete created user
    response = admin_router.delete_user(user_id)
    print(response.json())
    assert response.status_code==200

    #logout admin
    logout()


def test_create_user_with_exist_email():
    #login admin
    response = login()

    #create user (with no complete signup)
    response = admin_router.create_user(_user_email, _user_username, _user_password, False)
    print(response.json())
    assert response.status_code==201
    user_id = response.json()['id']

    #try to create user with exist email
    response = admin_router.create_user(_user_email, _user_username, _user_password, False)
    print(response.json())
    assert response.status_code==400
    assert ErrorCheck.check_locs(['email'], response.json())

    #Delete created user
    response = admin_router.delete_user(user_id)
    print(response.json())
    assert response.status_code==200

    #logout admin
    logout()


def test_set_user():
    #login admin
    response = login()

    #create user (with no complete signup)
    response = admin_router.create_user(_user_email, _user_username, _user_password, False)
    print(response.json())
    assert response.status_code==201
    user_id = response.json()['id']

    #set user username and complete signup
    response = admin_router.set_user(user_id, 'new_username_ssss', True)
    print(response.json())
    assert response.status_code==200

    #authenticate with user 
    response = router.authenticate(_user_email, _user_password)
    print(response.json())
    assert response.status_code==200

    #Delete created user
    response = admin_router.delete_user(user_id)
    print(response.json())
    assert response.status_code==200


#______________________PERMISSION_CRUD_TEST_________________________#

def _test_get_permission(id:str):
    #get permission informations
    response = admin_router.get_permission(id)
    print(response.json())
    assert response.status_code==200

    #try to get permission (not exist permision)
    response = admin_router.get_permission('sasadasdasdassd')
    print(response.json())
    assert response.status_code==404

    #get permissions
    response = admin_router.get_permissions()
    print(response.json())
    assert response.status_code==200


def test_create_permission():
    #login admin
    response = login()

    #create permission
    response = admin_router.create_permission(_permission1)
    print(response.json())
    assert response.status_code==201
    permission_id = response.json()['id']

    #try to create existed permission
    response = admin_router.create_permission(_permission1)
    print(response.json())
    assert response.status_code==400
    assert ErrorCheck.check_locs(['id'], response.json())

    #get permission
    _test_get_permission(permission_id)

    #delete permission
    response = admin_router.delete_permission(_permission1)
    print(response.json())
    assert response.status_code==200

    #try to delete a original permission
    response = admin_router.delete_permission('logout')
    print(response.json())
    assert response.status_code==403
    assert ErrorCheck.check_locs(['permission'], response.json())

    #logout admin
    logout()


#______________________GROUP_CRUD_TEST_________________________#

def _test_get_group(id:str):
    #get group informations
    response = admin_router.get_group(id)
    print(response.json())
    assert response.status_code==200

    #try to get group (not exist group)
    response = admin_router.get_group('sasadasdasdassd')
    print(response.json())
    assert response.status_code==404

    #get groups
    response = admin_router.get_groups()
    print(response.json())
    assert response.status_code==200


def test_create_group():
    #login admin
    response = login()

    #create group
    response = admin_router.create_group(_group)
    print(response.json())
    assert response.status_code==201
    group_id = response.json()['id']

    #try to create existed group
    response = admin_router.create_group(_group)
    print(response.json())
    assert response.status_code==400
    assert ErrorCheck.check_locs(['id'], response.json())

    #get group
    _test_get_group(group_id)

    #delete group
    response = admin_router.delete_group(_group)
    print(response.json())
    assert response.status_code==200

    #try to delete a original group
    response = admin_router.delete_group('normal')
    print(response.json())
    assert response.status_code==403
    assert ErrorCheck.check_locs(['group'], response.json())

    #logout admin
    logout()


#_________________________GRANT_TESTS________________________________________________#

def __authenticate_user():
    response = router.authenticate(_user_email, _user_password)
    print(response.json())
    assert response.status_code==200
    return response.json()['access_token']

def _test_grant_permission_to_user(user_id:str, permission_id:str):
    #grant permission to user
    response = admin_router.grant_permission_to_user(user_id, permission_id)
    print(response.json())
    assert response.status_code==200

    #try grant same permission again
    response = admin_router.grant_permission_to_user(user_id, permission_id)
    print(response.json())
    assert response.status_code==400
    assert ErrorCheck.check_locs(['user_permission'], response.json())

    #try grant not existed permission
    response = admin_router.grant_permission_to_user(user_id, 'blablabla')
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['permission_id'], response.json())

    #try grant not existed user
    response = admin_router.grant_permission_to_user(str(uuid.uuid4()), permission_id)
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['user_id'], response.json())


def _test_remove_permission_from_user(user_id:str, permission_id:str):
    #remove permission from user
    response = admin_router.remove_permission_from_user(user_id, permission_id)
    print(response.json())
    assert response.status_code==200

    #try to remove same permission again
    response = admin_router.remove_permission_from_user(user_id, permission_id)
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['user_permission'], response.json())

    #try to remove not existed permission
    response = admin_router.remove_permission_from_user(user_id, 'blablabla')
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['permission_id'], response.json())

    #try to remove not existed user
    response = admin_router.remove_permission_from_user(str(uuid.uuid4()), permission_id)
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['user_id'], response.json())


def _test_add_user_to_group(user_id:str, group_id:str):
    #add user to group
    response = admin_router.add_user_to_group(user_id, group_id)
    print(response.json())
    assert response.status_code==200

    #try add same user again
    response = admin_router.add_user_to_group(user_id, group_id)
    print(response.json())
    assert response.status_code==400
    assert ErrorCheck.check_locs(['user_group'], response.json())

    #try add not existed group
    response = admin_router.add_user_to_group(user_id, 'blablabla')
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['group_id'], response.json())

    #try add not existed user
    response = admin_router.add_user_to_group(str(uuid.uuid4()), group_id)
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['user_id'], response.json())


def _test_remove_user_from_group(user_id:str, group_id:str):
    #remove user from group
    response = admin_router.remove_user_from_group(user_id, group_id)
    print(response.json())
    assert response.status_code==200

    #try remove same user again
    response = admin_router.remove_user_from_group(user_id, group_id)
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['user_group'], response.json())

    #try remove not existed group
    response = admin_router.remove_user_from_group(user_id, 'blablabla')
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['group_id'], response.json())

    #try remove not existed user
    response = admin_router.remove_user_from_group(str(uuid.uuid4()), group_id)
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['user_id'], response.json())



def test_grant_permission_to_user():
    #login admin
    response = login()

    #create user (complete signup)
    response = admin_router.create_user(_user_email, _user_username, _user_password, True)
    print(response.json())
    assert response.status_code==201
    user_id = response.json()['id']

    #authenticate with user 
    access_token=__authenticate_user()

    #try to logout without logout permission
    response = router.logout(access_token)
    print(response.json())
    assert response.status_code==401
    
    #grant logout permission
    _test_grant_permission_to_user(user_id, 'logout')

    #authenticate with user 
    access_token=__authenticate_user()

    #logout
    response = router.logout(access_token)
    print(response.json())
    assert response.status_code==200

    #remove logout permission
    _test_remove_permission_from_user(user_id,'logout')

    #authenticate with user 
    access_token=__authenticate_user()

    #try logout without logout permission
    response = router.logout(access_token)
    print(response.json())
    assert response.status_code==401

    #Delete created user
    response = admin_router.delete_user(user_id)
    print(response.json())
    assert response.status_code==200

    #logout admin
    logout()


def test_group_permission_grant():
    #login admin
    response = login()

    #create group
    response = admin_router.create_group(_group)
    print(response.json())
    assert response.status_code==201
    group_id = response.json()['id']

    #grant logout permission to group
    response = admin_router.grant_permission_to_group(group_id, 'logout')
    print(response.json())
    assert response.status_code==200

    #create user (complete signup)
    response = admin_router.create_user(_user_email, _user_username, _user_password, True)
    print(response.json())
    assert response.status_code==201
    user_id = response.json()['id']

    #add user to created group
    _test_add_user_to_group(user_id, group_id)

    #authenticate with user 
    access_token=__authenticate_user()

    #logout
    response = router.logout(access_token)
    print(response.json())
    assert response.status_code==200
    
    #remove user from group
    _test_remove_user_from_group(user_id, group_id)

    #authenticate with user 
    access_token=__authenticate_user()

    #try logout without logout permisssion
    response = router.logout(access_token)
    print(response.json())
    assert response.status_code==401

    #try set username without set_own_username permission
    response = router.set_username(access_token, 'test_username', _user_password)
    print(response.json())
    assert response.status_code==401

    #add user to created group
    _test_add_user_to_group(user_id, group_id)

    #remove logout permission from group
    response = admin_router.remove_permission_from_group(group_id, 'logout')
    print(response.json())
    assert response.status_code==200

    #try remove logout permission from normal group (is original cant be deleted)
    response = admin_router.remove_permission_from_group('normal', 'logout')
    print(response.json())
    assert response.status_code==403
    assert ErrorCheck.check_locs(['group_permission'], response.json())


    #authenticate with user 
    access_token=__authenticate_user()

    #try logout without logout permission
    response = router.logout(access_token)
    print(response.json())
    assert response.status_code==401

    #Delete created user
    response = admin_router.delete_user(user_id)
    print(response.json())
    assert response.status_code==200

    #logout admin
    logout()


#________________SESSION_MANAGEMENT_TESTS_________________________________________#

def __authenticate_user_tokens():
    response = router.authenticate(_user_email, _user_password)
    print(response.json())
    assert response.status_code==200
    return response.json()

def _test_remove_session(access_token:str, one:bool):
    #get session_id and user_id
    response = client.post('/intra/authorization',json={'access_token':access_token})
    print(response.json())
    assert response.status_code==200
    user_id = response.json()['user_id']
    session_id = response.json()['session_id']

    if not one: session_id = None

    #remove session
    response = admin_router.remove_session(user_id, session_id)
    print(response.json())
    assert response.status_code==200


def test_remove_session():
    #login admin
    response = login()

    #create user (complete signup)
    response = admin_router.create_user(_user_email, _user_username, _user_password, True)
    print(response.json())
    assert response.status_code==201
    user_id = response.json()['id']

    #authenticate user 4 times
    tokens1 = __authenticate_user_tokens()
    tokens2 = __authenticate_user_tokens()
    tokens3 = __authenticate_user_tokens()
    tokens4 = __authenticate_user_tokens()

    #remove session 1
    _test_remove_session(tokens1['access_token'],True)

    #try refresh token (without session)
    response = router.refresh_token(tokens1['refresh_token'])
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['session'], response.json())

    #refresh token with sessio 2
    response = router.refresh_token(tokens2['refresh_token'])
    print(response.json())
    assert response.status_code==200

    #remove all others session
    _test_remove_session(tokens2['access_token'],False)

    #try refresh token with others sessions (without session)
    response = router.refresh_token(tokens3['refresh_token'])
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['session'], response.json())

    #Delete created user
    response = admin_router.delete_user(user_id)
    print(response.json())
    assert response.status_code==200