
data = {'update_time': '2019-01-12 00:00:00', 'size': '36M', 'installs': '100,000,000+', 'app_version': '1.3.3', 'min_os_version': '5.0 及更高版本', 'content_rating': '>适合所有人', 'provider': 'Serkan Özyılmaz', 'developer_email': 'magnificientgames2018@gmail.com', 'is_busy': 0, 'name': 'Rise Up', 'developer_url': 'https://play.google.com/store/apps/developer?id=Serkan+%C3%96zy%C4%B1lmaz', 'category': '街机', 'app_current_num': '1,122,124', 'cover_image_url': 'https://lh3.googleusercontent.com/n_3Q51HZ5v41am-EBPOjeU1hx5DS4KzG9KCJBbIenHKCYFhz6Rw6PTpxllkk-tkD4J4=s180-rw', 'description': "The most challenging and fun game of 2018! Protect your balloon with your shield while it's rising up! Beware of the obstacles.\n\nMove your shield with one finger to protect your balloon. Clear your way as you reach higher and higher!\n\nShield control is very easy but it's very hard to reach high scores!\n\nChallenge your friends for the highest score!\n\nGame Features:\n- Free to play\n- One finger control\n- Different obstacles and experience every time\n- Endless gameplay", 'what_news': '', 'pkgname': 'com.riseup.game', 'country': 'zh', 'url': 'https://play.google.com/store/apps/details?id=com.riseup.game&hl=zh&gl=us'}

# params = (data["country"], data["size"], data["category"], data["content_rating"],
#                           data["app_version"],
#                           data["description"], data["provider"], data["what_news"],
#                           data["developer_url"], data["installs"],
#                           data["is_busy"], data["update_time"], data["min_os_version"],
#                           data["name"], data["pkgname"], data["url"])
#
# sql = """
#
#                                 insert into crawl_google_play_app_info_zh (language,appsize,category,contentrating,current_version,description,developer,whatsnew,developer_url,instalations,isbusy,last_updatedate,minimum_os_version,name,pkgname,url) VALUES ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")
#                                 ON DUPLICATE KEY UPDATE appsize=VALUES(appsize),category=VALUES(category),contentrating=VALUES(contentrating),current_version=VALUES(current_version),
#                                 description=VALUES(description),developer=VALUES(developer),whatsnew=VALUES(whatsnew),
#                                 instalations=VALUES(instalations),last_updatedate=VALUES(last_updatedate),minimum_os_version=VALUES(minimum_os_version),name=VALUES(name)
# """
#
#
# print(sql.format(data["country"], data["size"], data["category"], data["content_rating"],
#                           data["app_version"],
#                           data["description"], data["provider"], data["what_news"],
#                           data["developer_url"], data["installs"],
#                           data["is_busy"], data["update_time"], data["min_os_version"],
#                           data["name"], data["pkgname"], data["url"]))


for i in data:
    data[i] = ""


print(data)