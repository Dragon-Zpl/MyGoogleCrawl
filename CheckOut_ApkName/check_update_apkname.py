import asyncio
import re
from datetime import datetime
from random import choice
from lxml import etree
from AllSetting import GetSetting
from AllSetting.mysql_setting import GetMysqlSetting
from CrawlProxy.ForeignProxyCrawl.crawl_foreigh_auto import crawl_fn


class CheckUpdateApkname:
    def __init__(self):
        self.setting = GetSetting()
        self.loop = self.setting.get_loop()
        self.session = self.setting.get_session()
        self.rcon = self.setting.get_redis()
        self.lock = asyncio.Lock()
        self.crawl_proxy = crawl_fn()
        self.apknames = set()
        self.proxies = []
        self.send_mysql = GetMysqlSetting()
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36",
        }
        self.country_dict = {
            # 'us': '&hl=en&gl=us',
            'ko': '&hl=ko&gl=us',
            'ar': '&hl=ar&gl=us',
            'jp': '&hl=ja&gl=us',
            'zh': '&hl=zh&gl=us',
            'zhtw': '&hl=zh_TW&gl=us',
        }

    async def get_redis_apk(self):
        async with self.lock:
            apk_detail = eval(self.rcon.brpop("download:queen", timeout=4)[1].decode('utf-8'))
            return apk_detail

    async def get_proxy(self):
        async with self.lock:
            if len(self.proxies) < 3:
                self.proxies = await self.crawl_proxy.run(self.session)
            try:
                proxy = choice(self.proxies)
                return proxy
            except:
                await self.get_proxy()

    def change_time(self, lang, LastUpdateDate):
        if LastUpdateDate:
            if lang == 'us':
                try:
                    LastUpdateDate = datetime.strptime(LastUpdateDate, '%B %d, %Y')
                except:
                    LastUpdateDate = re.findall('([0-9/])', LastUpdateDate)
                    LastUpdateDate = ''.join(LastUpdateDate)
                    LastUpdateDate = datetime.strptime(LastUpdateDate, '%m/%d/%Y')
            elif lang == 'ko':
                LastUpdateDate = datetime.strptime(LastUpdateDate, '%Y년 %m월 %d일')
            elif lang == 'ar':
                # arabic date need to be process specially
                LastUpdateDate = "2019-01-01 00:00:00"
            else:
                try:
                    LastUpdateDate = datetime.strptime(LastUpdateDate, '%Y年%m月%d日')
                except:
                    LastUpdateDate = "2019-01-01 00:00:00"
            return LastUpdateDate

    async def check_app_version(self, data, time=3, proxy=None):
        now_pkgname = data["pkgname"]
        now_app_version = data["app_version"]
        apk_url = "https://play.google.com/store/apps/details?id=" + now_pkgname
        if proxy == None:
            proxy = self.get_proxy()
        try:
            async with self.session.get(url=apk_url, headers=self.headers, proxy=proxy, timeout=10) as ct:
                if ct.status in [200, 201]:
                    datas = await ct.text()
                    analysis_data = self.analysis_web_data(datas)
                    analysis_data["country"] = "us"
                    analysis_data["pkgname"] = now_pkgname
                    analysis_data["url"] = apk_url
                    check_app_version = analysis_data["app_version"]
                    if check_app_version == now_app_version or check_app_version == None:
                        data_return = {}
                        data_return["app_version"] = now_app_version
                        data_return["pkgname"] = now_pkgname
                        data_return["is_update"] = 0
                    else:
                        data_return = {}
                        data_return["app_version"] = check_app_version
                        data_return["pkgname"] = now_pkgname
                        data_return["is_update"] = 1
                    return data_return, analysis_data
                elif ct.status in [403, 400, 500, 502, 503, 429]:
                    if time > 0:
                        proxy = await self.get_proxy()
                        return await self.check_app_version(data, proxy=proxy, time=time - 1)
                    else:
                        data_return = {}
                        data_return["app_version"] = now_app_version
                        data_return["pkgname"] = now_pkgname
                        data_return["is_update"] = 0
                        return data_return, None
        except:
            if time > 0:
                proxy = await self.get_proxy()
                return await self.check_app_version(data, proxy=proxy, time=time - 1)
            else:
                data_return = {}
                data_return["app_version"] = now_app_version
                data_return["pkgname"] = now_pkgname
                data_return["is_update"] = 0
                return data_return, None

    def analysis_web_data(self, data):
        analysis_dic = {}
        analysis_data = etree.HTML(data)
        xpath_list = analysis_data.xpath("//div[@class='hAyfc']")
        for xpath_one in xpath_list:
            needxpath = xpath_one.xpath(".//div[contains(@class,'BgcNfc')]")[0]
            # print('解析得到：'+ str(needxpath.xpath("./text()")[0]))
            if needxpath.xpath("./text()")[0] in ["更新日期", "업데이트 날짜", "تم التحديث", "更新日", "Updated"]:
                analysis_dic["update_time"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
            elif needxpath.xpath("./text()")[0] in ["大小", "크기", "الحجم", "サイズ", "Size"]:
                analysis_dic["size"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
            elif needxpath.xpath("./text()")[0] in ["当前版本", "현재 버전", "الإصدار الحالي", "現在のバージョン", "Current Version"]:
                analysis_dic["app_version"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
            elif needxpath.xpath("./text()")[0] in ["开发者", "제공", "تقديم", "提供元", "Offered By"]:
                analysis_dic["provider"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
            elif needxpath.xpath("./text()")[0] in ["콘텐츠 등급", "تقييم المحتوى", "コンテンツのレーティング", "Content Rating", "內容分級",
                                                    "内容分级"]:
                analysis_dic["content_rating"] = xpath_one.xpath(".//span[@class='htlgb']/div/text()")[0]
            elif needxpath.xpath("./text()")[0] in ["개발자", "مطوّر البرامج", "開発元", "Developer", "開發人員", "开发者"]:
                analysis_dic["developer_email"] = xpath_one.xpath(".//a[@class='hrTbp KyaTEc']/text()")[0]
            elif needxpath.xpath("./text()")[0] in ["설치 수", "عمليات التثبيت", "インストール", "Installs", "安裝次數", "安装次数"]:
                analysis_dic["installs"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
            elif needxpath.xpath("./text()")[0] in ["필요한 Android 버전", "يتطلب Android", "Android 要件", "Requires Android",
                                                    "Android 系统版本要求", "Android 最低版本需求"]:
                analysis_dic["min_os_version"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
                # print('是否购买：'+str(analysis_data.xpath("//span[@class='oocvOe']/button/@aria-label")[0]))
        # print('循环结束')
        if analysis_data.xpath("//span[@class='oocvOe']/button/@aria-label")[0] in ["安装", "설치", "تثبيت", "インストール",
                                                                                    "Install"]:
            analysis_dic["is_busy"] = 0
        else:
            analysis_dic["is_busy"] = 1
        analysis_dic["name"] = analysis_data.xpath("//h1[@class='AHFaub']/span/text()")[0]
        # print('analysis_dic["name"]'+analysis_dic["name"])
        analysis_dic["developer_url"] = analysis_data.xpath("//a[@class='hrTbp R8zArc']/@href")[0]
        # print('analysis_dic["developer_url"]'+analysis_dic["developer_url"])
        analysis_dic["category"] = analysis_data.xpath("//a[@itemprop='genre']/text()")[0]
        # print('analysis_dic["category"]'+analysis_dic["category"])
        analysis_dic["app_current_num"] = analysis_data.xpath("//span[@class='AYi5wd TBRnV']/span/text()")[0]
        # print('analysis_dic["app_current_num"]'+analysis_dic["app_current_num"])
        analysis_dic["cover_image_url"] = analysis_data.xpath("//div[@class='dQrBL']/img/@src")[0]
        # print('analysis_dic["cover_image_url"]'+analysis_dic["cover_image_url"])
        analysis_dic["description"] = analysis_data.xpath("//meta[@name='description']/@content")[0]
        analysis_dic["what_news"] = ','.join(analysis_data.xpath("//div[@class='DWPxHb']/content/text()"))
        return analysis_dic

    async def check_other_coutry(self, data, time=3, proxy=None):
        for country in self.country_dict:
            pkgname = data["pkgname"]
            apk_url = "https://play.google.com/store/apps/details?id=" + pkgname + self.country_dict[country]
            if proxy == None:
                proxy = self.get_proxy()
            try:
                async with self.session.get(url=apk_url, headers=self.headers, proxy=proxy, timeout=10) as ct:
                    if ct.status in [200, 201]:
                        datas = await ct.text()
                        check_app_data = self.analysis_web_data(datas)
                        check_app_data["pkgname"] = pkgname
                        check_app_data["country"] = country
                        check_app_data["url"] = apk_url
                        change_time = self.change_time(country, check_app_data["update_time"])
                        if change_time != None:
                            check_app_data["update_time"] = change_time

                        return check_app_data
                    elif ct.status in [403, 400, 500, 502, 503, 429]:
                        if time > 0:
                            proxy = await self.get_proxy()
                            return await self.check_other_coutry(data, proxy=proxy, time=time - 1)
                        else:
                            # fail_dict = {"pkgname": data["pkgname"], "update_time": "", "size": "",
                            #              "app_version": data["app_version"], "is_busy": "", "country": country,
                            #              "provider": "", "name": ""}
                            return None
            except:
                if time > 0:
                    proxy = await self.get_proxy()
                    return await self.check_other_coutry(data, proxy=proxy, time=time - 1)
                else:
                    # fail_dict = {"pkgname": data["pkgname"], "update_time": "", "size": "",
                    #              "app_version": data["app_version"], "is_busy": "", "country": country, "provider": "",
                    #              "name": ""}
                    return None

    async def save_redis(self, updatedata):
        data = {}
        data["pkgname"] = updatedata["pkgname"]
        data["app_version"] = updatedata["app_version"]
        data["host"] = "host"
        self.rcon.lpush("download:queen", str(data).encode('utf-8'))

    def run(self):
        tasks = []
        while True:
            task = asyncio.ensure_future(self.get_redis_apk())
            tasks.append(task)

            if len(tasks) > 20:
                results = self.loop.run_until_complete(asyncio.gather(*tasks))
                tasks = []
                check_tasks = []
                for result in results:
                    task = asyncio.ensure_future(self.check_app_version(result))
                    check_tasks.append(task)

                if len(check_tasks) >= 1:
                    check_results = self.loop.run_until_complete(asyncio.gather(*check_tasks))
                    redis_tasks = []
                    print('存入数据库')
                    save_mysql_tasks = []
                    check_other_tasks = []
                    for check_result in check_results:
                        try:
                            data_return, analysis_data = check_result
                            if data_return != None:
                                task = asyncio.ensure_future(self.save_redis(data_return))
                                redis_tasks.append(task)
                            if analysis_data != None:
                                print('添加数据库任务')
                                task = asyncio.ensure_future(self.send_mysql.run(self.loop,analysis_data))
                                save_mysql_tasks.append(task)
                            if data_return != None and data_return["is_update"] == 1:
                                task = asyncio.ensure_future(self.check_other_coutry(data_return))
                                check_other_tasks.append(task)
                        except Exception as e:
                            print('错误信息：' + str(e))
                            print(check_results)
                    if len(redis_tasks) >= 1:
                        self.loop.run_until_complete(asyncio.wait(redis_tasks))

                    if len(check_other_tasks) >= 1:
                        check_other_results = self.loop.run_until_complete(asyncio.gather(*check_other_tasks))
                        for result in check_other_results:
                            print("结果:" + str(result))
                            if result != None:
                                print("国家:" + result["country"])
                                task = self.send_mysql.run(self.loop,result)
                                save_mysql_tasks.append(task)

                    if len(save_mysql_tasks) >= 1:
                        print('执行存入数据库')
                        self.loop.run_until_complete(asyncio.wait(save_mysql_tasks))


if __name__ == '__main__':
    t = CheckUpdateApkname()
    t.run()
