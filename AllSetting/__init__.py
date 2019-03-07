import asyncio
import socket
import aiohttp
import redis


class GetSetting:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def get_loop(self):
        loop = asyncio.get_running_loop()
        if loop is None:
            loop = asyncio.get_event_loop()
        return loop

    def get_session(self):
        conn = aiohttp.TCPConnector(family=socket.AF_INET,
                                    verify_ssl=False,
                                    )
        session = aiohttp.ClientSession(connector=conn)
        return session

    def get_redis(self):
        pool = redis.ConnectionPool(host="192.168.9.227", password="a123456", port=6379, db=1)
        rcon = redis.Redis(connection_pool=pool)
        return rcon