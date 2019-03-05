import asyncio
from random import choice
from lxml import etree
from AllSetting import GetSetting
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
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36",
        }
        self.country_dict = {
            'us': '&hl=en&gl=us',
            'kr': '&hl=ko&gl=us',
            'sa': '&hl=ar&gl=us',
            'jp': '&hl=ja&gl=us',
            'zh': '&hl=zh&gl=us',
            'zh_tw': '&hl=zh_TW&gl=us',
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

    async def check_app_version(self, data, time=3, proxy=None):
        now_pkgname = data["pkgname"]
        now_app_version = data["app_version"]
        apk_url = "https://play.google.com/store/apps/details?id=" + now_pkgname
        if proxy == None:
            proxy = self.get_proxy()
        try:
            async with self.session.get(url=apk_url, headers=self.headers, proxy=proxy, timeout=10) as ct:
                print(ct.status)
                if ct.status in [200, 201]:
                    datas = await ct.text()
                    check_app_version = self.analysis_web_data(datas)["app_version"]
                    print('当前版本'+str(check_app_version))
                    if check_app_version == now_app_version:
                        pass
                    else:
                        data_return = {}
                        data_return["app_version"] = check_app_version
                        data_return["pkgname"] = now_pkgname
                        data_return["is_update"] = 1
                        return data_return
                elif ct.status in [403, 400, 500, 502, 503, 429]:
                    if time > 0:
                        proxy = await self.get_proxy()
                        return await self.check_app_version(data, proxy=proxy, time=time - 1)
                    else:
                        data_return = {}
                        data_return["app_version"] = now_app_version
                        data_return["pkgname"] = now_pkgname
                        data_return["is_update"] = 0
                        return data_return
        except:
            if time > 0:
                proxy = await self.get_proxy()
                return await self.check_app_version(data, proxy=proxy, time=time - 1)
            else:
                data_return = {}
                data_return["app_version"] = now_app_version
                data_return["pkgname"] = now_pkgname
                data_return["is_update"] = 0
                return data_return

    def analysis_web_data(self, data):
        print('进入解析')
        analysis_dic = {}
        analysis_data = etree.HTML(data)
        xpath_list = analysis_data.xpath("//div[@class='hAyfc']")
        for xpath_one in xpath_list:
            print(needxpath.xpath("./text()")[0])
            needxpath = xpath_one.xpath("./div")
            if needxpath.xpath("./text()")[0] == ["更新日期", "업데이트 날짜", "تم التحديث", "更新日", "Updated"]:
                analysis_data["update_time"] = needxpath.xpath(".//span[@class='htlgb']/text()")[0]
            elif needxpath.xpath("./text()")[0] == ["大小", "크기", "الحجم", "サイズ", "Size"]:
                analysis_data["size"] = needxpath.xpath(".//span[@class='htlgb']/text()")[0]
            elif needxpath.xpath("./text()")[0] == ["当前版本", "현재 버전", "الإصدار الحالي", "現在のバージョン", "Current Version"]:
                analysis_data["app_version"] = needxpath.xpath(".//span[@class='htlgb']/text()")[0]
            elif needxpath.xpath("./text()")[0] == ["开发者", "제공", "تقديم", "提供元", "Offered By"]:
                analysis_data["provider"] = needxpath.xpath(".//span[@class='htlgb']/text()")[0]
        if analysis_data.xpath("//span[@class='oocvOe']/button/@aria-label")[0] in ["安装", "설치", "تثبيت", "インストール"]:
            analysis_dic["is_busy"] = 0
        else:
            analysis_dic["is_busy"] = 1
        analysis_dic["name"] = analysis_data.xpath("//h1[@class='AHFaub']/span/text()")
        print(analysis_dic)
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
                        return check_app_data
                    elif ct.status in [403, 400, 500, 502, 503, 429]:
                        if time > 0:
                            proxy = await self.get_proxy()
                            return await self.check_other_coutry(data, proxy=proxy, time=time - 1)
                        else:
                            fail_dict = {"pkgname": data["pkgname"], "update_time": "", "size": "",
                                         "app_version": data["app_version"], "is_busy": "", "country": country,
                                         "provider": "", "name": ""}
                            return fail_dict
            except:
                if time > 0:
                    proxy = await self.get_proxy()
                    return await self.check_other_coutry(data, proxy=proxy, time=time - 1)
                else:
                    fail_dict = {"pkgname": data["pkgname"], "update_time": "", "size": "",
                                 "app_version": data["app_version"], "is_busy": "", "country": country, "provider": "",
                                 "name": ""}
                    return fail_dict

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

            if len(tasks) > 100:
                results = self.loop.run_until_complete(asyncio.gather(*tasks))
                tasks = []
                check_tasks = []
                for result in results:
                    task = asyncio.ensure_future(self.check_app_version(result))
                    check_tasks.append(task)

                check_results = self.loop.run_until_complete(asyncio.gather(*check_tasks))

                redis_tasks = []
                print('存入数据库')
                for check_result in check_results:
                    print(check_result)
                    if check_result != None:
                        task = asyncio.ensure_future(self.save_redis(check_result))
                        redis_tasks.append(task)

                if len(redis_tasks) >= 1:
                    self.loop.run_until_complete(asyncio.wait(redis_tasks))

                check_other_tasks = []
                print('查询其他国家')
                for check_result in check_results:
                    if check_result["is_update"] == 1:
                        task = asyncio.ensure_future(self.check_other_coutry(check_result))
                        check_other_tasks.append(task)

                if len(check_other_tasks) >= 1:
                    check_other_results = self.loop.run_until_complete(asyncio.gather(*check_other_tasks))

                for result in check_other_results:
                    print('其他国家结果' + str(result))


if __name__ == '__main__':
    t = CheckUpdateApkname()
    t.run()