import aiomysql
import asyncio

class GetMysqlSetting:
    def __init__(self):
        pass

    async def insert_mysql(self,loop,data):
        pool = await aiomysql.create_pool(host='192.168.9.227',port=3306,user='root',password='123456',db='google_play',charset='utf8',autocommit=True,loop=loop)
        async with pool.get() as conn:
            async with conn.cursor() as cur:
                if data["country"] == "us":
                    to_mysql = "crawl_google_play_app_info"
                else:
                    to_mysql = "crawl_google_play_app_info_" + data["country"]
                sql = 'insert into ' + to_mysql + '(id,language,appsize,category,contentrating,current_version,description,developer,whatsnew,developer_url,instalations,isbusy,last_updatedate,minimum_os_version,name,pkgname,url) VALUES(default,"{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format(data["country"], data["size"], data["category"], data["content_rating"],
                                           data["app_version"],
                                           data["description"], data["provider"], data["what_news"],
                                           data["developer_url"], data["installs"],
                                           data["is_busy"], data["update_time"], data["min_os_version"],
                                           data["name"], data["pkgname"], data["url"])
                try:
                    await cur.execute(sql)
                except Exception as e:
                    print('数据库错误信息：' + str(e))


    def run(self,loop,data):
        task = asyncio.ensure_future(self.insert_mysql(loop,data))
        return task
if __name__ == '__main__':
    t = GetMysqlSetting()
    t.run()