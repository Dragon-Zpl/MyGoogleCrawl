import asyncio

import aiomysql

data = {'pkgname':'test','url':'test','country': 'us', 'update_time': '2019-02-28 00:00:00', 'size': '36M', 'installs': '1,000,000+', 'app_version': '36.7.6', 'min_os_version': '4.0 and up', 'content_rating': 'Everyone', 'provider': 'Dialekts', 'developer_email': 'dialekts.game@gmail.com', 'is_busy': 0, 'name': 'Shoot Dinosaur Eggs', 'developer_url': 'https://play.google.com/store/apps/developer?id=Dialekts', 'category': 'Casual', 'app_current_num': '4,478', 'cover_image_url': 'https://lh3.googleusercontent.com/OHew4iL5WhbpvZ-oAvr8-wPQ-_N77SvaAOfCzkGeUruYPuDx1gTScEmrXy1nlcwvGEk=s180-rw', 'description': 'Configure the combination and shoot down the balls of the same color. The game has many different levels, with each new level to knock the egg becomes more difficult.', 'what_news': '✔ Added adaptive icon.,✔ We have improved performance.,✔ Fixed bugs.,Thanks for playing. Be sure to rate us after each update.'}


async def insert_mysql(data):
    pool = await aiomysql.create_pool(host='192.168.9.227', port=3306, user='root', password='123456', db='google_play',
                                      charset='utf8', autocommit=True)
    return pool
loop = asyncio.get_event_loop()
loop.run_until_complete(insert_mysql(data))