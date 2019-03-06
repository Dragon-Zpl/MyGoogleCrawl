import redis
pool = redis.ConnectionPool(host="192.168.9.227", password="a123456", port=6379, db=1)
rcon = redis.Redis(connection_pool=pool)
data = {'app_version': '1.0.7', 'pkgname': 'com.twenty48.solitaire.merge.card.merge2048','host':'0'}
# rcon.rpush("download:queen",str(data).encode('utf-8'))

rcon.zadd("download:queen",1,str(data).encode('utf-8'))

# print(rcon.get())