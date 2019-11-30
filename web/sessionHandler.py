import redis
import hashlib
import datetime
from uuid import uuid4


class SessionHandler:
    def __init__(self, redisConnection):
        self.redisConnection = redisConnection

    def createSession(self, login):
        id = str(uuid4())
        sessionTime = datetime.datetime.now() + datetime.timedelta(minutes=5)
        sessionTime = str(sessionTime)
        self.redisConnection.hset('sessionTime', id, sessionTime)
        self.redisConnection.hset('sessionLogin', id, login)
        return id

    def checkSession(self, id):
        session = self.redisConnection.hget('sessionLogin', id)
        if session is not None:
            expTime = datetime.datetime.strptime(self.redisConnection.hget('sessionTime', id).decode("UTF-8"),
                                                 '%Y-%m-%d %H:%M:%S.%f')
            if expTime > datetime.datetime.now():
                return True
        return False

    def deleteSession(self, id):
        self.redisConnection.hdel('sessionTime', id)
        self.redisConnection.hdel('sessionLogin', id)

    def getNicknameSession(self, id):
        return self.redisConnection.hget('sessionLogin', id).decode("UTF-8")
