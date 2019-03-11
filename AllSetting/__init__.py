import asyncio
import socket
import aiohttp
import redis
import logging.handlers

class GetSetting:
    def __init__(self):
        pass
    def get_loop(self):
        loop = asyncio.get_event_loop()
        return loop

    def get_session(self):
        conn = aiohttp.TCPConnector(family=socket.AF_INET,
                                    verify_ssl=False,
                                    use_dns_cache=True
                                    )
        session = aiohttp.ClientSession(connector=conn)
        return session

    def get_redis(self):
        pool = redis.ConnectionPool(host="192.168.9.227", password="a123456", port=6379, db=1)
        rcon = redis.Redis(connection_pool=pool)
        return rcon

    def get_logger(self,info):
        logger = logging.getLogger('project')  # 不加名称设置root logger
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(filename)s - %(lineno)s %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        # 使用FileHandler输出到文件
        fh = logging.handlers.TimedRotatingFileHandler('log.txt',when='D',interval=1)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        # 使用StreamHandler输出到屏幕
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        # 添加两个Handler
        logger.addHandler(ch)
        logger.addHandler(fh)
        return logger.info(info)