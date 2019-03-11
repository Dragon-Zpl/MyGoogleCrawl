import asyncio
import time
from random import choice
from AllSetting import GetSetting
from CrawlProxy.ForeignProxyCrawl.crawl_foreigh_auto import crawl_fn
from Database_Option.Get_Mysql_pool import GetMysqlPool
from Database_Option.redis_option import RedisOption
from Parsing import ParsingData
from Request_Web.AllRequest import InitiateRequest


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
        self._Request = InitiateRequest()
        self.apknames = set()
        self.proxies = []
        self.all_data_list = []
        self.printf = self.setting.get_logger
        self.country_dict = {
            # 'us': '&hl=en&gl=us',
            'zh': '&hl=zh&gl=us',
            'zhtw': '&hl=zh_TW&gl=us',
            'ko': '&hl=ko&gl=us',
            'ar': '&hl=ar&gl=us',
            'jp': '&hl=ja&gl=us',
        }

    async def _get_proxy(self):
        async with self.lock:
            if len(self.proxies) < 3:
                self.proxies = await self.crawl_proxy.run(self.session)
            try:
                proxy = choice(self.proxies)
                return proxy
            except:
                await self._get_proxy()

    async def check_app_version(self, data, time=3, proxy=None):
        """
        检查美国的版本是否更新
        """
        now_pkgname = data["pkgname"]
        now_app_version = await self.get_pool.find_pkgname(now_pkgname)
        apk_url = "https://play.google.com/store/apps/details?id=" + now_pkgname
        for i in range(3):
            if proxy is None:
                proxy = await self._get_proxy()
            try:
                datas = await self._Request.get_request(self.session,apk_url,proxy)
                if datas:
                    analysis_data = self.parsing.analysis_country_data(datas)
                    # 判断是否已经可下载
                    if analysis_data is None:
                        data_return = {}
                        data_return["pkgname"] = now_pkgname
                        data_return["is_update"] = 0
                        return data_return, None
                    analysis_data["country"] = "us"
                    analysis_data["pkgname"] = now_pkgname
                    analysis_data["url"] = apk_url
                    check_app_version = analysis_data["app_version"]
                    change_time = self.parsing.change_time('us', analysis_data["update_time"])
                    if change_time is not None:
                        analysis_data["update_time"] = change_time
                    # 数据库中版本不为空，且检查版本与数据库相同或者检查版本为空时，不更新
                    if now_app_version is not None and (check_app_version == now_app_version or check_app_version is None):
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
                else:
                    self.printf("data is none")
            except Exception as e:
                if str(e) == "":
                    self.printf("错误数据"+str(data))
                self.printf(str(e))
        else:
            # 失败三次重新放入redis中
            self.printf('失败三次重新放入redis')
            data_return = {}
            data_return["pkgname"] = now_pkgname
            data_return["is_update"] = 2
            return data_return, None

    async def check_other_coutry(self, data, time=3, proxy=None):
        '''
        获取其他国家的数据
        '''
        for country in self.country_dict:
            pkgname = data["pkgname"]
            apk_url = "https://play.google.com/store/apps/details?id=" + pkgname + self.country_dict[country]
            if proxy == None:
                proxy = await self._get_proxy()
            for i in range(3):
                try:
                    datas = await self._Request.get_request(self.session, apk_url, proxy)
                    if datas:
                        check_app_data = self.parsing.analysis_country_data(datas)
                        if check_app_data is None:
                            break
                        check_app_data["pkgname"] = pkgname
                        check_app_data["country"] = country
                        check_app_data["url"] = apk_url
                        change_time = self.parsing.change_time(country, check_app_data["update_time"])
                        if change_time is not None:
                            check_app_data["update_time"] = change_time
                        self.all_data_list.append(check_app_data)
                        break
                except Exception as e:
                    if str(e) == "":
                        self.printf("错误数据" + str(data))
                    self.printf(str(e))
            else:
                return None

    def _get_pkgdata_redis(self,start):
        """
        从redis中获取pkg的数据
        """
        pkg_datas = []
        for i in range(100):
            end = time.time()
            if (end -start) > 20:
                return pkg_datas
            pkg_data = self.get_redis.get_redis_pkgname()
            pkg_datas.append(pkg_data)
        return pkg_datas

    def _build_check_tasks(self, results):
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

    def _task_ensure_future(self, func, data, tasks):
        task = asyncio.ensure_future(func(data))
        tasks.append(task)

    def _build_other_insert(self, check_results):
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
                if data_return is not None and data_return["is_update"] == 2:
                    self.get_redis.update_pkgname_redis(data_return)
                if analysis_data is not None:
                    self._task_ensure_future(self.get_pool.insert_mysql_, analysis_data, save_mysql_tasks)
                if data_return is not None and data_return["is_update"] == 1:
                    self._task_ensure_future(self.check_other_coutry, data_return, check_other_tasks)
            except Exception as e:
                self.printf('错误信息：' + str(e))
        return save_mysql_tasks, check_other_tasks

    def run(self):
        """
        从redis中获取pkg数据->检查美国的包是否有更新->更新redis->以美国为基准获取其他国家有版本更新的包的数据->存入数据库
        """
        while True:
            start = time.time()
            pkg_datas = self._get_pkgdata_redis(start)
            check_tasks = self._build_check_tasks(pkg_datas)
            if len(check_tasks) >= 1:
                check_results = self.loop.run_until_complete(asyncio.gather(*check_tasks))
                save_mysql_tasks, check_other_tasks = self._build_other_insert(check_results)
                if len(check_other_tasks) >= 1:
                    self.loop.run_until_complete(asyncio.wait(check_other_tasks))
                    for result_list in self.all_data_list:
                        if result_list is not None:
                            task = self.get_pool.insert_mysql_(result_list)
                            save_mysql_tasks.append(task)
                    self.all_data_list = []
                if len(save_mysql_tasks) >= 1:
                    self.loop.run_until_complete(asyncio.wait(save_mysql_tasks))
