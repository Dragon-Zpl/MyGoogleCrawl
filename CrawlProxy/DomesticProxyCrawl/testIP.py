import redis
pool = redis.ConnectionPool(host="192.168.9.227", password="a123456", port=6379, db=1)
rcon = redis.Redis(connection_pool=pool)

dic ={"pkgname":'test',"app_version":'dsad',"host":'das'}
rcon.lpush("download:queen",str(dic).encode('utf-8'))
