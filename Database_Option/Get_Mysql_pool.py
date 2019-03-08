import aiomysql

class GetMysqlPool:
    def __init__(self):
        self._host = '192.168.9.227'
        self._port = 3306
        self._user = 'root'
        self._password = '123456'
        self._db = 'google_play'

        self.pool = await aiomysql.create_pool(host=self._host, port=self._port, user=self._user, password=self._password,
                                      db=self._db, charset='utf8', autocommit=True)

    async def insert_mysql(self, data):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                if data["country"] == "us":
                    to_mysql = "crawl_google_play_app_info"
                else:
                    to_mysql = "crawl_google_play_app_info_" + data["country"]
                sql_google = """

                                        insert into {} (language,appsize,category,contentrating,current_version,description,developer,whatsnew,developer_url,instalations,isbusy,last_updatedate,minimum_os_version,name,pkgname,url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                        ON DUPLICATE KEY UPDATE appsize=VALUES(appsize),category=VALUES(category),contentrating=VALUES(contentrating),current_version=VALUES(current_version),
                                        description=VALUES(description),developer=VALUES(developer),whatsnew=VALUES(whatsnew),
                                        instalations=VALUES(instalations),last_updatedate=VALUES(last_updatedate),minimum_os_version=VALUES(minimum_os_version),name=VALUES(name)
        """.format(to_mysql)
                params = (data["country"], data["size"], data["category"], data["content_rating"],
                          data["app_version"],
                          data["description"], data["provider"], data["what_news"],
                          data["developer_url"], data["installs"],
                          data["is_busy"], data["update_time"], data["min_os_version"],
                          data["name"], data["pkgname"], data["url"])
                try:
                    result = await cur.execute(sql_google, params)
                except Exception as e:
                    print("数据库语句:" + sql_google)
                    print("错误时候的数据"+str(data))
                    print('数据库错误信息：' + str(e))