import asyncio

import aiomysql

data = {'pkgname':'test','url':'test','country': 'us', 'update_time': '2019-02-28 00:00:00', 'size': '36M', 'installs': '1,000,000+', 'app_version': '36.7.6', 'min_os_version': '4.0 and up', 'content_rating': 'Everyone', 'provider': 'Dialekts', 'developer_email': 'dialekts.game@gmail.com', 'is_busy': 0, 'name': 'Shoot Dinosaur Eggs', 'developer_url': 'https://play.google.com/store/apps/developer?id=Dialekts', 'category': 'Casual', 'app_current_num': '4,478', 'cover_image_url': 'https://lh3.googleusercontent.com/OHew4iL5WhbpvZ-oAvr8-wPQ-_N77SvaAOfCzkGeUruYPuDx1gTScEmrXy1nlcwvGEk=s180-rw', 'description': 'Configure the combination and shoot down the balls of the same color. The game has many different levels, with each new level to knock the egg becomes more difficult.', 'what_news': '✔ Added adaptive icon.,✔ We have improved performance.,✔ Fixed bugs.,Thanks for playing. Be sure to rate us after each update.'}


async def insert_mysql(loop, data):
    pool = await aiomysql.create_pool(host='192.168.9.227', port=3306, user='root', password='123456', db='google_play',
                                      charset='utf8', autocommit=True, loop=loop)
    async with pool.get() as conn:
        async with conn.cursor() as cur:
            if data["country"] == "us":
                to_mysql = "crawl_google_play_app_info"
            else:
                to_mysql = "crawl_google_play_app_info_" + data["country"]
            sql = 'insert into ' + to_mysql + '(id,language,appsize,category,contentrating,current_version,description,developer,whatsnew,developer_url,instalations,isbusy,last_updatedate,minimum_os_version,name,pkgname,url) VALUES(default,"{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format(
                data["country"], data["size"], data["category"], data["content_rating"],
                data["app_version"],
                data["description"], data["provider"], data["what_news"],
                data["developer_url"], data["installs"],
                data["is_busy"], data["update_time"], data["min_os_version"],
                data["name"], data["pkgname"], data["url"])
            try:
                await cur.execute(sql)
                print('执行成功')
            except Exception as e:
                print("数据库语句:" + sql)
                print('数据库错误信息：' + str(e))

loop = asyncio.get_event_loop()
loop.run_until_complete(insert_mysql(loop,data))