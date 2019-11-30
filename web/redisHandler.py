import redis
import hashlib


class RedisHandler:
    def __init__(self, redisConnection):
        self.redisConnection = redisConnection

    def initUser(self):
        self.redisConnection.hset('account', "test", "123")
        self.redisConnection.hset('account', "Jeremi", "Wisniowiecki")
        self.redisConnection.hset('account', "Stanislaw", "Moniuszko")
        self.redisConnection.hset('account', "Tadeusz", "Mazowiecki")
        self.redisConnection.hset('account', "Apoloniusz", "Tajner")
        self.redisConnection.hset('account', "Romuald", "Traugutt")

    def checkUser(self, login, password):
        if self.redisConnection.hget('account', login) is None:
            return False
        if self.redisConnection.hget('account', login).decode("UTF-8") != password:
            return False
        return True
