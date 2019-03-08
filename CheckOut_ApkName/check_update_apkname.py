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
        self.loop.run_until_complete(asyncio.ensure_future(self.get_pool.init_pool()))
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
        """
        检查美国的版本是否更新
        """
        now_pkgname = data["pkgname"]
        now_app_version = data["app_version"]
        apk_url = "https://play.google.com/store/apps/details?id=" + now_pkgname
        for i in range(3):
            if proxy == None:
                proxy = await self.get_proxy()
            try:
                async with self.session.get(url=apk_url, headers=self.headers, proxy=proxy, timeout=10) as ct:
                    if ct.status in [200, 201]:
                        datas = await ct.text()
                        analysis_data = self.parsing.analysis_country_data(datas,now_pkgname)
                        # 判断是否已经可下载
                        if analysis_data == None:
                            data_return = {}
                            data_return["app_version"] = now_app_version
                            data_return["pkgname"] = now_pkgname
                            data_return["is_update"] = 0
                            return data_return, None
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
                        pass
            except Exception as e:
                print("更新错误的数据"+str(data))
                print("更新错误:"+str(e))
        else:
            data_return = {}
            data_return["app_version"] = now_app_version
            data_return["pkgname"] = now_pkgname
            data_return["is_update"] = 0
            return data_return, None



    async def check_other_coutry(self, data, time=3, proxy=None):
        '''
        获取其他国家的数据
        '''
        for country in self.country_dict:
            pkgname = data["pkgname"]
            apk_url = "https://play.google.com/store/apps/details?id=" + pkgname + self.country_dict[country]
            if proxy == None:
                proxy = await self.get_proxy()
            for i in range(3):
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
                            break
                        elif ct.status in [403, 400, 500, 502, 503, 429]:
                            pass
                except Exception as e:
                    print("错误信息的数据"+str(data))
                    print('错误信息:'+str(e))
            else:
                return None

    def get_pkgdata_redis(self):
        """
        从redis中获取pkg的数据
        """
        pkg_datas = []
        for i in range(50):
            pkg_data = self.get_redis.get_redis_pkgname()
            pkg_datas.append(pkg_data)
        return pkg_datas

    def build_check_tasks(self, results):
        '''
        创建检查美国信息的任务队列
        :param results:
        :return: 需要检查并要存入redis的pkg数据的字典,需要存入mysql美国的pkg数据的字典(两个字典)
        '''
        check_tasks = []
        for result in results:
            task = asyncio.ensure_future(self.check_app_version(result))
            check_tasks.append(task)
        return check_tasks

    def task_ensure_future(self, func, data, tasks):
        task = asyncio.ensure_future(func(data))
        tasks.append(task)

    def build_other_insert(self, check_results):
        '''
        遍历以美国为基准的需要更新的数据，分别更新redis, 创建检查其他国家的任务队列和将美国数据插入mysql的任务队列
        :param check_results:
        :return: 存入mysql的任务队列和检查其他国家的任务队列
        '''

        save_mysql_tasks = []
        check_other_tasks = []
        for check_result in check_results:
            try:
                data_return, analysis_data = check_result
                if data_return != None:
                    self.get_redis.update_pkgname_redis(data_return)
                if analysis_data != None:
                    self.task_ensure_future(self.get_pool.insert_mysql, analysis_data, save_mysql_tasks)
                if data_return != None and data_return["is_update"] == 1:
                    self.task_ensure_future(self.check_other_coutry, data_return, check_other_tasks)
            except Exception as e:
                print('错误信息：' + str(e))
        return save_mysql_tasks, check_other_tasks

    def run(self):
        """
        从redis中获取pkg数据->检查美国的包是否有更新->更新redis->以美国为基准获取其他国家有版本更新的包的数据->存入数据库
        """
        while True:
            pkg_datas = self.get_pkgdata_redis()
            check_tasks = self.build_check_tasks(pkg_datas)
            if len(check_tasks) >= 1:
                check_results = self.loop.run_until_complete(asyncio.gather(*check_tasks))
                save_mysql_tasks, check_other_tasks = self.build_other_insert(check_results)
                if len(check_other_tasks) >= 1:
                    self.loop.run_until_complete(asyncio.wait(check_other_tasks))
                    for result_list in self.all_data_list:
                        if result_list != None:
                            task = self.get_pool.insert_mysql(result_list)
                            save_mysql_tasks.append(task)
                    self.all_data_list = []
                if len(save_mysql_tasks) >= 1:
                    self.loop.run_until_complete(asyncio.wait(save_mysql_tasks))
