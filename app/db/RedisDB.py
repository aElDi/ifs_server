from ..config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from redis import Redis

class RedisDB():
    def __init__(self, host: str, port: int, password: str) -> None:
        self._client = Redis(host, port, password=password, decode_responses=True)
    
    def getSession(self, key: str):
        return self._client.get(f'sessions:{key}')
    
    def addSession(self, key: str, value: str):
        return self._client.set(f'sessions:{key}', value)
    
    def addConfirmRay(self, rayid:str, code: int, username: str):
        return self._client.hset(f"keys:{rayid}", mapping={
            "conf_code": code,
            "username": username
        })
    
    def getConfirmRay(self, rayid:str):
        return self._client.hgetall(f'keys:{rayid}')
    
    def removeConfirmRay(self, rayid: str):
        self._client.delete(f"keys:{rayid}")

redisdb = RedisDB(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)