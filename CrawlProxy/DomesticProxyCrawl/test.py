import redis
from lxml import etree
from random import choice
import aiohttp
import socket

import asyncio
import re


class crawl_fn:
    def __init__(self):

        self.headers_foreign_gather = {
            'Host': "www.gatherproxy.com",  # 需要修改为当前网站主域名
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
        }

        self.headers_foreign_other = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'www.us-proxy.org',
            'If-Modified-Since': 'Tue, 24 Jan 2017 03:32:01 GMT',
            'Referer': 'http://www.sslproxies.org/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"
        }
        self.headers_normal = {
            'User_Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
        }

        self.number = 0

    async def check_proxy(self,session,proxy_info):
        if self.number <= 20:
            proxy = 'http://' + str(proxy_info["ip"]) + ':' + str(proxy_info["port"])

            try:
                async with session.get(url="https://google.com", proxy=proxy, headers=self.headers_normal,
                                       timeout=4) as res:
                    if res.status == 200:
                        print('可用的'+str(self.number)+'proxy'+str(proxy))
                        self.number += 1
                        return proxy
                    else:
                        return None
            except Exception as e:
                return None

    async def get_useful_proxy(self, session):
        proxies = []
        await self.get_ori_proxy(session,proxies)

        tasks = []
        proxies = tuple(proxies)
        for proxy_info in proxies:
            task = asyncio.ensure_future(self.check_proxy(session,proxy_info))
            tasks.append(task)
        return await asyncio.gather(*tasks)

    async def get_ori_proxy(self,session,proxies):
        tasks = [asyncio.ensure_future(self.get_foreign_proxy(session,proxies))]
        await asyncio.gather(*tasks)

    async def get_foreign_proxy(self, session, proxies):
        url = "http://www.gatherproxy.com"
        code = await self.get_request(url, session, self.headers_foreign_gather)
        if code:
            self.analysis_code(code, proxies)

    async def get_request(self, url, session, headers):
         try:
             async with session.get(url=url, headers=headers, timeout=4) as ct:
                 if ct.status == 200:
                     code = await ct.text()
                     return code
         except Exception as e:
             print(e)

    def analysis_code(self,code,proxies):
        re_str = '(?<=insertPrx\().*\}'
        proxy_list = re.findall(re_str, code)
        null = ''
        for i in proxy_list:
            ip_dic = {}
            json_list = eval(i)
            ip_dic["ip"] = json_list['PROXY_IP']
            PROXY_PORT = json_list['PROXY_PORT']
            ip_dic["port"] = int(PROXY_PORT, 16)
            ip_dic["country"] = json_list['PROXY_COUNTRY']
            ip_dic["last_update"] = json_list['PROXY_LAST_UPDATE']
            ip_dic["time"] = json_list['PROXY_TIME']
            ip_dic["uptimeld"] = json_list['PROXY_UPTIMELD']
            proxies.append(ip_dic)

    async def run(self,session):
        proxies = []
        results = await self.get_useful_proxy(session)

        for result in results:
            if result != None:
                proxies.append(result)

        return proxies



class GetSetting:
    def __init__(self):
        pass

    def get_loop(self):
        loop = asyncio.get_event_loop()
        return loop

    def get_session(self):
        conn = aiohttp.TCPConnector(family=socket.AF_INET,
                                    verify_ssl=False,
                                    )
        session = aiohttp.ClientSession(connector=conn)
        return session

    def get_redis(self):
        pool = redis.ConnectionPool(host="192.168.9.227", password="a123456", port=6379, db=1)
        rcon = redis.Redis(connection_pool=pool)
        return rcon

class CrawlApkName:
    def __init__(self):
        self.apk_names = set()
        self.son_category_url = set()
        self.session = GetSetting().get_session()
        self.crawl_proxy = crawl_fn()
        self.loop = GetSetting().get_loop()
        self.lock = asyncio.Lock()
        self.rcon = GetSetting().get_redis()
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36",
        }

        self.proxies = []

        self.host = "https://play.google.com/"

        self.urls = {
            'url_newgame_free': 'https://play.google.com/store/apps/category/GAME/collection/topselling_new_free?authuser=0',
            # new热门免费游戏 post url
            'url_newcolletion_free': 'https://play.google.com/store/apps/collection/topselling_new_free?authuser=0',
            # # new热门免费应用
            "url_app_topsell": "https://play.google.com/store/apps/collection/topselling_free",
            'url_paid_topcol': 'https://play.google.com/store/apps/collection/topselling_paid?authuser=0',
            'url_topgross_col': 'https://play.google.com/store/apps/collection/topgrossing?authuser=0',
            'url_topgame_free': 'https://play.google.com/store/apps/category/GAME/collection/topselling_free?authuser=0',
            'url_topgross_game': 'https://play.google.com/store/apps/category/GAME/collection/topgrossing?authuser=0',
            "url_new_app": "https://play.google.com/store/apps/collection/topselling_new_free",
            "url_new_game": "https://play.google.com/store/apps/category/GAME/collection/topselling_new_free",
        }

    def get_apknames_tasks(self):
        tasks = []
        for url in self.urls.values():
            post_data_first = {
                'ipf': '1',
                'xhr': '1'
            }
            task = asyncio.ensure_future(self.fetch_post_apkname(url, post_data_first))
            tasks.append(task)
            for i in range(1, 20):
                post_data = {
                    'start': i * 60,
                    'num': '60',
                    'numChildren': '0',
                    'cctcss': 'square-cover',
                    'cllayout': 'NORMAL',
                    'ipf': '1',
                    'xhr': '1',
                }
                task = asyncio.ensure_future(self.fetch_post_apkname(url, post_data))
                tasks.append(task)
        return tasks


    def build_async_tasks(self,urls):
        tasks = []
        for url in urls:
            task = asyncio.ensure_future(self.get_web_data(url))
            tasks.append(task)
        return tasks

    async def fetch_post_apkname(self,url,data):
        proxy = await self.get_proxy()
        try:
            async with self.session.post(url=url, data=data, headers=self.headers, proxy=proxy, timeout=10) as ct:
                data = await ct.text()
                analysis_data = etree.HTML(data)
                apknames = analysis_data.xpath(
                    "//div[@class='card no-rationale square-cover apps small']//span[@class='preview-overlay-container']/@data-docid")
                for apkname in apknames:
                    self.apk_names.add(apkname)
        except Exception as e:
            try:
                self.proxies.remove(proxy)
            except:
                pass



    async def fetch_get_apkname(self,url):
        print('fetch_get_apkname')
        proxy = await self.get_proxy()
        try:
            async with self.session.get(url=url, headers=self.headers, proxy=proxy, timeout=10) as ct:
                data = await ct.text()
                analysis_data = etree.HTML(data)
                apknames = analysis_data.xpath(
                    "//div[@class='card no-rationale square-cover apps small']//span[@class='preview-overlay-container']/@data-docid")
                for apkname in apknames:
                    print(apkname)
                    self.apk_names.add(apkname)
        except:
            try:
                self.proxies.remove(proxy)
            except:
                pass
    async def get_category_url(self, data):
        analysis_data = etree.HTML(data)
        urls = analysis_data.xpath("//div[@class='dropdown-submenu']//a/@href")
        urls = [self.host + url for url in urls]
        feasible_url = set()
        for url in urls:
            print('category:'+str(url))
            if "GAME" in url or "SOCIAL" in url or "SPORTS" in url or "SHOPPING" in url or "HEALTH_AND_FITNESS" in url or "COMICS" in url:
                feasible_url.add(url)
        return feasible_url

    async def get_proxy(self):
        async with self.lock:
            if len(self.proxies) < 3:
                self.proxies = await self.crawl_proxy.run(self.session)
            try:
                proxy = choice(self.proxies)
                print('输出可以用的proxy' + str(proxy))
                return proxy
            except:
                await self.get_proxy()

    async def get_web_data(self, url):
        print('get_web_data')
        proxy = await self.get_proxy()
        try:
            async with self.session.get(url=url, headers=self.headers, proxy=proxy, timeout=5) as ct:
                data = await ct.text()
                return data
        except:
            try:
                self.proxies.remove(proxy)
            except:
                pass

    async def get_main_url(self):
        print('get_main_url')
        proxy = await self.get_proxy()
        url = "https://play.google.com/store/apps"
        try:
            async with self.session.get(url=url, headers=self.headers, proxy=proxy, timeout=5) as tc:
                data = await tc.text()
                analysis_data = etree.HTML(data)
                urls = analysis_data.xpath("//div[@class='g4kCYe']/a/@href")
                return urls
        except:
            try:
                self.proxies.remove(proxy)
            except:
                pass

    async def save_redis(self,apkname):
        data = {}
        data["pkgname"] = apkname
        data["app_version"] = "none"
        data["host"] = "host"
        self.rcon.rpush("download:queen",str(data).encode('utf-8'))

    def run(self):
        self.apk_names.clear()
        # 获取最外层的apkname
        tasks = self.get_apknames_tasks()

        self.loop.run_until_complete(asyncio.wait(tasks))

        # 获取最外层类别的url，共八种
        print('进入外层')
        urls = self.loop.run_until_complete(self.get_main_url())

        tasks = self.build_async_tasks(urls)

        results = self.loop.run_until_complete(asyncio.gather(*tasks))
        # 获取里层的分类的url

        task = asyncio.ensure_future(self.get_category_url(results[0]))


        allurls = self.loop.run_until_complete(task)

        print('进入子层')
        for url in allurls:
            print('子url'+str(url))
            self.son_category_url.add(url)

        get_apkname_tasks = []
        print('进入最后一层')
        for url in self.son_category_url:
            task = asyncio.ensure_future(self.fetch_get_apkname(url))
            get_apkname_tasks.append(task)

        self.loop.run_until_complete(asyncio.gather(*get_apkname_tasks))

        save_redis_tasks = []

        for apkname in self.apk_names:
            task = asyncio.ensure_future(self.save_redis(apkname))
            save_redis_tasks.append(task)

        self.loop.run_until_complete(asyncio.wait(save_redis_tasks))
if __name__ == '__main__':
    t = CrawlApkName()
    t.run()