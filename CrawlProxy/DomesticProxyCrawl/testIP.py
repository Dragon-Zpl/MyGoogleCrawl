
data = {'update_time': '2019-01-01 00:00:00', 'size': '76M', 'installs': '+5,000,000', 'app_version': '2.2.5', 'min_os_version': '4.1 والأحدث', 'content_rating': 'مراهقون', 'provider': 'International Games System Co., Ltd.', 'developer_email': 'service@igsgame.com.tw', 'is_busy': 0, 'name': 'Golden HoYeah Slots - Casino Slots', 'developer_url': 'https://play.google.com/store/apps/developer?id=International+Games+System+Co.,+Ltd.', 'category': 'كازينو', 'app_current_num': '227,652', 'cover_image_url': 'https://lh3.googleusercontent.com/yBT-FQxFoHGizsQFIZT11I4jALvBpZX5KduAfNt--gVhdH0UiKSVOziaimjOvA-yCQ=s180-rw', 'description': "testdes", 'what_news': 'test', 'pkgname': 'com.igs.fafafa', 'country': 'ar', 'url': 'https://play.google.com/store/apps/details?id=com.igs.fafafa&hl=ar&gl=us'}

params = (data["country"], data["size"], data["category"], data["content_rating"],
                          data["app_version"],
                          data["description"], data["provider"], data["what_news"],
                          data["developer_url"], data["installs"],
                          data["is_busy"], data["update_time"], data["min_os_version"],
                          data["name"], data["pkgname"], data["url"])

sql = """

                                insert into crawl_google_play_app_info_ar (language,appsize,category,contentrating,current_version,description,developer,whatsnew,developer_url,instalations,isbusy,last_updatedate,minimum_os_version,name,pkgname,url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                ON DUPLICATE KEY UPDATE appsize=VALUES(appsize),category=VALUES(category),contentrating=VALUES(contentrating),current_version=VALUES(current_version),
                                description=VALUES(description),developer=VALUES(developer),whatsnew=VALUES(whatsnew),
                                instalations=VALUES(instalations),last_updatedate=VALUES(last_updatedate),minimum_os_version=VALUES(minimum_os_version),name=VALUES(name)
"""


print(sql.format(data["country"], data["size"], data["category"], data["content_rating"],
                          data["app_version"],
                          data["description"], data["provider"], data["what_news"],
                          data["developer_url"], data["installs"],
                          data["is_busy"], data["update_time"], data["min_os_version"],
                          data["name"], data["pkgname"], data["url"]))