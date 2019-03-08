
data = {'update_time': '2019-02-27 00:00:00', 'size': '因设备而异', 'installs': '1,000,000+', 'app_version': '1.3.3', 'min_os_version': '4.1 及更高版本', 'content_rating': '适合所有人', 'provider': 'solo puzzle game free', 'developer_email': 'dasolaiconnat@gmail.com', 'is_busy': 0, 'name': '塊寶石拼圖遊戲  塊拼圖瘋狂傳奇 2019', 'developer_url': 'https://play.google.com/store/apps/developer?id=solo+puzzle+game+free', 'category': '益智', 'app_current_num': '4,134', 'cover_image_url': 'https://lh3.googleusercontent.com/wRO5DrMqcIbXCXG75J7LBrZWTVENK7RWtKGDrKCy3SjaPh4MEVsxQsp0oYopZwzLJC8=s180-rw', 'description': '塊寶石拼圖遊戲塊拼圖瘋狂傳奇2019很簡單但又好笑又上癮！\n讓我們用這款免費的經典寶石益智遊戲探索寶石之地吧！玩這款珠寶拼圖遊戲時，你將無法將視線從屏幕上移開。\n\n塊寶石拼圖遊戲塊拼圖瘋狂傳奇2019遊戲特色\n- 令人驚嘆的寶石和鑽石圖形\n- 驚人的效果和生動的聲音\n- 無需互聯網連接，完全免費\n- 簡單的遊戲，但很難輕鬆獲得高分\n- 沒有時間和等級限制。這個寶石挑戰是無限的\n\n怎麼玩\n- 將寶石塊拖放到屏幕中的適當位置\n- 在屏幕充滿寶石塊之前，盡量製作盡可能多的寶石線\n- 獲得的分數越多，您可以實現的寶石線越多\n- 寶石益智遊戲將不會結束，直到下面框中的下一個寶石塊沒有空位\n- 隨時隨地停止這個無限的寶石挑戰，但當你停止這個經典遊戲時，你必須再次啟動塊益智遊戲並重置分數。', 'what_news': '', 'pkgname': 'com.puzzlegamefree.blockpuzzle.gems.jewel', 'country': 'zh', 'url': 'https://play.google.com/store/apps/details?id=com.puzzlegamefree.blockpuzzle.gems.jewel&hl=zh&gl=us'}


params = (data["country"], data["size"], data["category"], data["content_rating"],
                          data["app_version"],
                          data["description"], data["provider"], data["what_news"],
                          data["developer_url"], data["installs"],
                          data["is_busy"], data["update_time"], data["min_os_version"],
                          data["name"], data["pkgname"], data["url"])

sql = """

                                insert into crawl_google_play_app_info_zh (language,appsize,category,contentrating,current_version,description,developer,whatsnew,developer_url,instalations,isbusy,last_updatedate,minimum_os_version,name,pkgname,url) VALUES ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")
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