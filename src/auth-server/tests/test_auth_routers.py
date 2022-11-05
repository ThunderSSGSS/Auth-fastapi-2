from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError
from typing import List
import time

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from app.main import app


client = TestClient(app)

_email = 'example@gmail.com'
_new_email = 'example2@gmail.com'
_password = 'example1234'
_new_password = 'example12345'
_username = 'example'
_random='12345'

#____________ERROR_JSON_VALIDATOR___________________________#
class OneError(BaseModel):
    loc:List[str]
    msg:str
    type:str

class ErrorValidator(BaseModel):
    detail:List[OneError]

    @classmethod
    def is_valid(cls, data:dict):
        try: p = cls.parse_obj(data)
        except ValidationError as ex: return False
        return True

class ErrorCheck():
    @classmethod
    def _search_loc(cls, loc:str, locs:list):
        for loc2 in locs: 
            if loc==loc2: return True
        return False
    
    @classmethod
    def check_locs(cls, locs:list, error_dict:dict):
        errors = error_dict['detail']
        found = False
        for loc in locs:
            for error in errors:
                if cls._search_loc(loc, error['loc']): 
                    found=True
                    break
            if found: found=False
            else: return False
        return True


#_____________AUTH_ROUTERS___________________________________#

class AuthRouter():
    def __init__(self, client:TestClient=client):
        self._client = client

    def signup(self, email:str, username:str, password:str):
        data={'username':username, 'email':email, 'password':password}
        return self._client.post('/auth/signup', json=data)

    def logout(self, access_token:str):
        return self._client.post('/auth/logout', headers = {'Authorization':'Bearer '+access_token})

    def complete_signup(self, email:str, password:str, random:str):
        data = {'email':email, 'password':password, 'random':random}
        return self._client.post('/auth/signup/complete', json=data)

    def regenerate_signup_random(self, email:str):
        return self._client.post('/auth/random/regenerate/signup', json={'email':email})

    def authenticate(self, email:str, password:str):
        return self._client.post('/auth/authenticate', json={'email':email, 'password':password})

    def refresh_token(self, refresh_token:str):
        return self._client.post('/auth/refresh', json={'refresh_token':refresh_token})

    def forget_password(self, email:str):
        return self._client.post('/auth/password/forget', json={'email':email})

    def restaure_password(self, email:str, new_password:str, random:str):
        return self._client.post('/auth/password/restaure', json={'email':email, 
            'new_password':new_password, 'random':random})

    def regenerate_password_random(self, email:str):
        return self._client.post('/auth/random/regenerate/password', json={'email':email})

    def set_password(self, new_password:str, password:str, access_token:str):
        return self._client.post('/auth/password/set', headers = {'Authorization':'Bearer '+access_token},
            json={'new_password':new_password, 'password':password})

    def set_email(self, new_email:str, password:str, access_token:str):
        return self._client.post('/auth/email/set', headers = {'Authorization':'Bearer '+access_token},
            json={'new_email':new_email, 'password':password})

    def complete_set_email(self, random:str, access_token):
        return self._client.post('/auth/email/set/complete', headers = {'Authorization':'Bearer '+access_token},
            json={'random':random})

    def regenerate_email_random(self, access_token:str):
        return self._client.post('/auth/random/regenerate/email', headers = {'Authorization':'Bearer '+access_token})
    
    def admin_get_users(self, access_token:str):
        return self._client.get('/admin/users', headers = {'Authorization':'Bearer '+access_token})

    def get_user_data(self, access_token:str):
        return self._client.get('/auth/user/data', headers = {'Authorization':'Bearer '+access_token})
    
    def set_username(self, access_token:str, new_username:str, password:str):
        return self._client.post('/auth/username/set', headers = {'Authorization':'Bearer '+access_token},
            json={'password':password, 'new_username':new_username})



#_________________TESTS_AUTH_ROUTERS________________________________________#

router = AuthRouter()

#_________SIGNUP_FLOW_TEST________________#

def test_signup_flow():
    #signup
    response = router.signup(_email, _username, _password)
    assert response.status_code==200

    #complete signup
    response = router.complete_signup(_email, _password, _random)
    print(response.json())
    assert response.status_code==200
    access_token = response.json()['access_token']
    refresh_token = response.json()['refresh_token']

    #logout
    response = router.logout(access_token)
    print(response.json())
    assert response.status_code==200

def test_signup_exist_email():
    response = router.signup(_email, _username, _password)
    print(response.json())
    assert response.status_code==400
    assert ErrorCheck.check_locs(['email'], response.json())

def test_regenerate_signup_random_with_user_completed():
    response = router.regenerate_signup_random(_email)
    print(response.json())
    assert response.status_code==400
    assert ErrorCheck.check_locs(['signup'], response.json())


#_________AUTHENTICATE_TEST_______________________#

def test_authentication_refresh_token_logout():
    #authenticate
    response = router.authenticate(_email, _password)
    print(response.json())
    assert response.status_code==200
    refresh_token = response.json()['refresh_token']
    access_token = response.json()['access_token']

    #try to access a unauthorized resource
    response = router.admin_get_users(access_token)
    print(response.json())
    assert response.status_code==401
    assert ErrorCheck.check_locs(['access_token'], response.json())

    #refresh_token
    response = router.refresh_token(refresh_token)
    print(response.json())
    assert response.status_code==200
    access_token = response.json()['access_token']

    #logout
    response = router.logout(access_token)
    print(response.json())
    assert response.status_code==200

    #refresh_token with no session
    response = router.refresh_token(refresh_token)
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['session'], response.json())


#______FORGET_PASSWORD_FLOW_and_SET_PASSWORD__________#

def test_forget_password_flow():
    #forget password
    response = router.forget_password(_email)
    print(response.json())
    assert response.status_code==200
    
    #restaure password
    response = router.restaure_password(_email, _password, _random)
    print(response.json())
    assert response.status_code==200

    #regenerate password random without random
    response = router.regenerate_password_random(_email)
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['random'], response.json())


#_______SET_PASSWORD___________________#

def test_set_password():
    #authenticate
    response = router.authenticate(_email, _password)
    print(response.json())
    assert response.status_code==200
    access_token = response.json()['access_token']

    #set password
    response = router.set_password(_new_password, _password, access_token)
    print(response.json())
    assert response.status_code==200

    #logout
    response = router.logout(access_token)
    print(response.json())
    assert response.status_code==200


#_______SET_EMAIL_FLOW__________________#

def test_email_flow():
    #authenticate
    response = router.authenticate(_email, _new_password)
    print(response.json())
    assert response.status_code==200
    access_token = response.json()['access_token']

    #set email
    response = router.set_email(_new_email, _new_password, access_token)
    print(response.json())
    assert response.status_code==200

    #complete set email
    response = router.complete_set_email(_random, access_token)
    print(response.json())
    assert response.status_code==200

    #regenerate email random without random
    response = router.regenerate_email_random(access_token)
    print(response.json())
    assert response.status_code==404
    assert ErrorCheck.check_locs(['random'], response.json())


#_________GET_USER__TEST__________#
def test_get_user_data():
    #authenticate
    response = router.authenticate(_new_email, _new_password)
    print(response.json())
    assert response.status_code==200
    access_token = response.json()['access_token']

    #get_user data
    response = router.get_user_data(access_token)
    print(response.json())
    assert response.status_code==200

#_________SET_USERNAME_TEST__________#
def test_set_username():
    #authenticate
    response = router.authenticate(_new_email, _new_password)
    print(response.json())
    assert response.status_code==200
    access_token = response.json()['access_token']

    #set username
    response = router.set_username(access_token, 'test_username', _new_password)
    print(response.json())
    assert response.status_code==200

    #get user data to check username
    response = router.get_user_data(access_token)
    print(response.json())
    assert response.status_code==200
    assert response.json()['username']=='test_username'