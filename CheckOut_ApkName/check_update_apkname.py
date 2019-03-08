import asyncio
from random import choice
from AllSetting import GetSetting
from CrawlProxy.ForeignProxyCrawl.crawl_foreigh_auto import crawl_fn
from Database_Option.Get_Mysql_pool import GetMysqlPool
from Database_Option.redis_option import RedisOption
from Parsing import ParsingData


class CheckUpdateApkname:
    def __init__(self):
        self.setting = GetSetting()
        self.loop = self.setting.get_loop()
        self.session = self.setting.get_session()
        self.lock = asyncio.Lock()
        self.crawl_proxy = crawl_fn()
        self.parsing = ParsingData()
        self.get_pool = GetMysqlPool()
        self.get_redis = RedisOption()
        self.apknames = set()
        self.proxies = []
        self.all_data_list = []
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36",
        }
        self.country_dict = {
            # 'us': '&hl=en&gl=us',
            'zh': '&hl=zh&gl=us',
            'zhtw': '&hl=zh_TW&gl=us',
            'ko': '&hl=ko&gl=us',
            'ar': '&hl=ar&gl=us',
            'jp': '&hl=ja&gl=us',
        }

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
                if ct.status in [200, 201]:
                    datas = await ct.text()
                    analysis_data = self.parsing.analysis_country_data(datas)
                    analysis_data["country"] = "us"
                    analysis_data["pkgname"] = now_pkgname
                    analysis_data["url"] = apk_url
                    check_app_version = analysis_data["app_version"]
                    change_time = self.parsing.change_time('us', analysis_data["update_time"])
                    if change_time != None:
                        analysis_data["update_time"] = change_time
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
                        check_app_data = self.parsing.analysis_country_data(datas)
                        check_app_data["pkgname"] = pkgname
                        check_app_data["country"] = country
                        check_app_data["url"] = apk_url
                        change_time = self.parsing.change_time(country, check_app_data["update_time"])
                        if change_time != None:
                            check_app_data["update_time"] = change_time
                        self.all_data_list.append(check_app_data)
                    elif ct.status in [403, 400, 500, 502, 503, 429]:
                        if time > 0:
                            proxy = await self.get_proxy()
                            return await self.check_other_coutry(data, proxy=proxy, time=time - 1)
                        else:
                            return None
            except:
                if time > 0:
                    proxy = await self.get_proxy()
                    return await self.check_other_coutry(data, proxy=proxy, time=time - 1)
                else:
                    return None

    def build_asyncio_tasks(self):
        tasks = []
        for i in range(50):
            task = asyncio.ensure_future(self.get_redis.get_redis_pkgname())
            tasks.append(task)
        return tasks

    def build_check_tasks(self, results):
        check_tasks = []
        for result in results:
            task = asyncio.ensure_future(self.check_app_version(result))
            check_tasks.append(task)
        return check_tasks

    def build_other_insert(self, check_results):
        redis_tasks = []
        save_mysql_tasks = []
        check_other_tasks = []
        for check_result in check_results:
            try:
                data_return, analysis_data = check_result
                if data_return != None:
                    task = asyncio.ensure_future(self.get_redis.update_pkgname_redis(data_return))
                    redis_tasks.append(task)
                if analysis_data != None:
                    task = asyncio.ensure_future(self.get_pool.insert_mysql(analysis_data))
                    save_mysql_tasks.append(task)
                if data_return != None and data_return["is_update"] == 1:
                    task = asyncio.ensure_future(self.check_other_coutry(data_return))
                    check_other_tasks.append(task)
            except Exception as e:
                print('错误信息：' + str(e))
        return redis_tasks, save_mysql_tasks, check_other_tasks

    def run(self):
        while True:
            tasks = self.build_asyncio_tasks()
            results = self.loop.run_until_complete(asyncio.gather(*tasks))
            check_tasks = self.build_check_tasks(results)
            if len(check_tasks) >= 1:
                check_results = self.loop.run_until_complete(asyncio.gather(*check_tasks))
                redis_tasks, save_mysql_tasks, check_other_tasks = self.build_other_insert(check_results)
                if len(redis_tasks) >= 1:
                    self.loop.run_until_complete(asyncio.wait(redis_tasks))
                if len(check_other_tasks) >= 1:
                    self.loop.run_until_complete(asyncio.wait(check_other_tasks))
                    for result_list in self.all_data_list:
                        if result_list != None:
                            task = self.get_pool.insert_mysql(result_list)
                            save_mysql_tasks.append(task)
                    self.all_data_list = []
                if len(save_mysql_tasks) >= 1:
                    self.loop.run_until_complete(asyncio.wait(save_mysql_tasks))
