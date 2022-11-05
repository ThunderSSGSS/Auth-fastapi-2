import aiohttp
from fastapi import Request, Depends, HTTPException
from .settings import AUTHORIZATION_URL
import json




async def _make_request(url:str, data:dict):
	async with aiohttp.ClientSession() as session:
		async with session.post(url, data=json.dumps(data), 
			headers={'Content-Type':'application/json'}) as response:
			result={'status':response.status}
			result['json']=await response.json()
			return result

def _unauthorizate_exception():
	return HTTPException(status_code=401, 
		detail={'loc':['Authorization'], 'msg':'unauthorized', 'type':'unauthorized'})
	
async def _check_authorization(req: Request, permissions:list, groups:list):
	if "Authorization" in req.headers:
		data = {'access_token':req.headers['Authorization'],
			'permissions':permissions, 'groups':groups}
		
		result = await _make_request(AUTHORIZATION_URL, data)
		if result['status'] !=200: 
			raise HTTPException(result['status'], result['json'])
		else: return result['json']
	raise HTTPException(status_code=400, detail='Authentication not provited')

#______________CHECK_PERMISSIONS_____________________#
async def check_admin_permission(req: Request):
	return await _check_authorization(req,['admin'],[])