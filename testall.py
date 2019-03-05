from AllSetting import GetSetting

a = GetSetting()

# rcon = a.get_redis()

# data = {"pkgname":"test","app_version":"123","host":"23.236.115.227"}
#
# rcon.rpush("download:queen", str(data).encode('utf-8'))
#
# a = rcon.brpop("download:queen")
a = (b'download:queen', b"{'pkgname': 'test', 'app_version': '123', 'host': '23.236.115.227'}")
b = eval(a[1].decode('utf-8'))


print(b.values())