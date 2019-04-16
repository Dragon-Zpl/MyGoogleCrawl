import redis


class RedisOption:
    def __init__(self):
        self._host = ''
        self._password = ''
        self._port = 6379
        self._db = 1
        self.rcon = self._get_redis()

    def _get_redis(self):
        pool = redis.ConnectionPool(host=self._host, password=self._password, port=self._port, db=self._db)
        rcon = redis.Redis(connection_pool=pool)
        return rcon

    def save_pkgname_redis(self, apkname):
        """
        将pkg数据存入redis
        """
        data = {}
        data["pkgname"] = apkname
        data["host"] = "host"
        self.rcon.sadd("pkgname", str(data).encode('utf-8'))

    def update_pkgname_redis(self, updatedata):
        """
        更新redis中的pkg数据
        """
        data = {}
        data["pkgname"] = updatedata["pkgname"]
        data["host"] = "host"
        self.rcon.sadd("pkgname", str(data).encode('utf-8'))

    def get_redis_pkgname(self):
        """
        从redis的获取一个pkg数据并返回
        """
        apk_detail = eval(self.rcon.spop("pkgname").decode('utf-8'))
        return apk_detail
