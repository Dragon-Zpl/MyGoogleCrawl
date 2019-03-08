import redis


class RedisOption:
    def __init__(self):
        self._host = '192.168.9.227'
        self._password = 'a123456'
        self._port = 6379
        self._db = 1
        self.rcon = self._get_redis()

    def _get_redis(self):
        pool = redis.ConnectionPool(host=self._host, password=self._password, port=self._port, db=self._db)
        rcon = redis.Redis(connection_pool=pool)
        return rcon

    def save_pkgname_redis(self, apkname):
        data = {}
        data["pkgname"] = apkname
        data["app_version"] = "none"
        data["host"] = "host"
        self.rcon.rpush("download:queen", str(data).encode('utf-8'))

    def update_pkgname_redis(self, updatedata):
        data = {}
        data["pkgname"] = updatedata["pkgname"]
        data["app_version"] = updatedata["app_version"]
        data["host"] = "host"
        self.rcon.lpush("download:queen", str(data).encode('utf-8'))

    async def get_redis_pkgname(self):
        apk_detail = eval(self.rcon.brpop("download:queen", timeout=4)[1].decode('utf-8'))
        return apk_detail