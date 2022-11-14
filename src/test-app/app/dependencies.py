import aiohttp
from fastapi import Request, Depends, HTTPException
from .settings import AUTHORIZATION_URL
import json
# Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


_security = HTTPBearer()

def _get_token_from_header(credentials: HTTPAuthorizationCredentials= Depends(_security)):
	return credentials.credentials

async def _make_request(url:str, data:dict):
	async with aiohttp.ClientSession() as session:
		async with session.post(url, data=json.dumps(data), 
			headers={'Content-Type':'application/json'}) as response:
			result={'status':response.status}
			result['json']=await response.json()
			return result
	
async def _check_authorization(access_token:str, permissions:list, groups:list):
	data = {'access_token':access_token,'permissions':permissions, 'groups':groups}
	result = await _make_request(AUTHORIZATION_URL, data)
	if result['status'] !=200: 
		raise HTTPException(result['status'], result['json'])
	else: return result['json']

#______________CHECK_PERMISSIONS_____________________#
async def check_admin_permission(token:str = Depends(_get_token_from_header)):
	return await _check_authorization(token,['admin'],[])