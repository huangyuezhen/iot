
import redis

from conf import settings


class _Redis():
    def __init__(self,settings):

        self.host = settings["host"]
        self.port = settings["port"]
        self.password =  settings["password"]

    def connection_pool(self):
        pool = redis.ConnectionPool(host=self.host, port=self.port, password=self.password)
        return  pool

Redis = _Redis(settings['redis'])



