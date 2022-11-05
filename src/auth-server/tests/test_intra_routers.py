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

_email='useruser@gmail.com'
_username='useruser'
_password='example#'


#_____________INTRA_ROUTERS___________________________________#

class IntraRouter():
    def __init__(self, client:TestClient=client):
        self._client = client

    def get_status(self):
        return self._client.get('/intra/status')

    def check_authorization(self, access_token:str, permissions:list, groups:list):
        return self._client.post('/intra/authorization',
            json={'access_token':access_token, 'permissions':permissions, 'groups':groups})


#_________________TESTS_INTRA_ROUTERS________________________________________#

router = AuthRouter(client)
intra_router = IntraRouter()


def _user_signup_flow():
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

    return access_token, refresh_token


#_____REAL_TESTS_________#

def test_get_status():
    response = intra_router.get_status()
    print(response.json())
    assert response.status_code==200

def test_check_authorization():
    access_token, refresh_token = _user_signup_flow()

    #check permissions
    response = intra_router.check_authorization(access_token, ['set_own_email','set_own_password'],[])
    print(response.json())
    assert response.status_code==200

    #check permissions and groups
    response = intra_router.check_authorization(access_token, ['set_own_email','set_own_password'],['normal'])
    print(response.json())
    assert response.status_code==200

    #try to check permissions and wrong groups
    response = intra_router.check_authorization(access_token, ['set_own_email','set_own_password'],['admin'])
    print(response.json())
    assert response.status_code==401
    assert ErrorCheck.check_locs(['access_token'], response.json())

    #try to check wrong permissions and groups
    response = intra_router.check_authorization(access_token, ['set_own_email','admin'],['normal'])
    print(response.json())
    assert response.status_code==401
    assert ErrorCheck.check_locs(['access_token'], response.json())

    #try to check wrong access_token
    response = intra_router.check_authorization(refresh_token, ['set_own_email','admin'],['normal'])
    print(response.json())
    assert response.status_code==403
    assert ErrorCheck.check_locs(['access_token'], response.json())