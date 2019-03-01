import asyncio
import socket
import aiohttp

class GetSetting:
    def __init__(self):
        pass

    def get_loop(self):
        loop = asyncio.get_event_loop()
        return loop

    def get_session(self):
        conn = aiohttp.TCPConnector(family=socket.AF_INET,
                                    verify_ssl=False,
                                    # use_dns_cache=True
                                    )
        session = aiohttp.ClientSession(connector=conn)
        return session
