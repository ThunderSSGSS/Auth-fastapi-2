import json
from datetime import timedelta
from app.internal.settings import CACHE, AUTH
from app.internal.adapter.interfaces import CacheRepositoryInterface


_PREFIX = CACHE['PREFIX']
_SESSION_EXP = AUTH['ACCESS_TOKEN_EXP'] + AUTH['REFRESH_TOKEN_EXP']
CACHE_URI = CACHE['CACHE_URI']

#_________BASE_REDIS_CACHE_CRUD_________________#

class BaseAsyncRedisCache(CacheRepositoryInterface):
	element_prefix=None
	element_expire=None

	def __init__(self, session, root_prefix=_PREFIX):
		self._redis = session
		self._root_prefix = root_prefix

	def _add_prefix(self, key:str):
		return self._root_prefix+':'+self.element_prefix+':'+key

	async def set(self, key:str, value, expire:float=0):
		#value, must be a object that json can serialize
		keyP = self._add_prefix(key)
		if expire==0: expire = self.element_expire
		await self._redis.setex(keyP,timedelta(minutes=expire),value=json.dumps(value))

	def _serializer_result(self, result:str):
		if result is not None: return json.loads(result)
		return result

	async def get(self, key:str):
		keyP = self._add_prefix(key)
		return self._serializer_result(await self._redis.get(keyP))

	async def delete(self, key:str):
		keyP = self._add_prefix(key)
		await self._redis.delete(keyP)


#_________________IMPLEMENTATIONS____________________________#

class SessionCache(BaseAsyncRedisCache):
	element_prefix='session'
	element_expire= _SESSION_EXP