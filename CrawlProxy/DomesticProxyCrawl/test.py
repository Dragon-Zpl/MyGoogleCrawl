
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
         async with session.get(url=url, headers=headers, timeout=4) as ct:
             if ct.status == 200:
                 code = await ct.text()
                 return code

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


class CrawlApkName:
    def __init__(self):
        self.apk_names = set()
        self.son_category_url = set()
        self.session = GetSetting().get_session()
        self.crawl_proxy = crawl_fn()
        self.loop = GetSetting().get_loop()
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
        print('get_apknames_tasks')
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
        print('build_async_tasks')
        tasks = []
        for url in urls:
            task = asyncio.ensure_future(self.get_web_data(url))
            tasks.append(task)
        return tasks

    async def fetch_post_apkname(self,url,data):
        print('fetch_post_apkname')
        proxy = await self.get_proxy()
        try:
            async with self.session.post(url=url, data=data, headers=self.headers, proxy=proxy) as ct:
                print(ct.status)
                data = await ct.text()
                analysis_data = etree.HTML(data)
                apknames = analysis_data.xpath(
                    "#//div[@class='card no-rationale square-cover apps small']//span[@class='preview-overlay-container']/@data-docid")
                for apkname in apknames:
                    print('apkname'+apkname)
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
            async with self.session.get(url=url, headers=self.headers, proxy=proxy) as ct:
                data = await ct.text()
                analysis_data = etree.HTML(data)
                apknames = analysis_data.xpath(
                    "#//div[@class='card no-rationale square-cover apps small']//span[@class='preview-overlay-container']/@data-docid")
                for apkname in apknames:
                    print(apkname)
                    self.apk_names.add(apkname)
        except:
            try:
                self.proxies.remove(proxy)
            except:
                pass
    async def get_category_url(self, data):
        print('get_category_url')
        analysis_data = etree.HTML(data)
        urls = analysis_data.xpath("//div[@class='dropdown-submenu']//a/@href")
        urls = [self.host + url for url in urls]
        feasible_url = set()
        for url in urls:
            print(url)
            if "GAME" in url or "SOCIAL" in url or "SPORTS" in url or "SHOPPING" in url or "HEALTH_AND_FITNESS" in url or "COMICS" in url:
                feasible_url.add(url)
        return feasible_url

    async def get_proxy(self):
        print('get_proxy')
        if len(self.proxies) < 3:
            self.proxies = await self.crawl_proxy.run(self.session)
        proxy = choice(self.proxies)
        try:
            print('输出可以用的proxy'+str(proxy))
            return proxy
        except:
            self.get_proxy()

    async def get_web_data(self, url):
        print('get_web_data')
        proxy = await self.get_proxy()
        try:
            async with self.session.get(url=url, headers=self.headers, proxy=proxy, timeout=10) as ct:
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
            async with self.session.get(url=url, headers=self.headers, proxy=proxy) as tc:
                data = await tc.text()
                analysis_data = etree.HTML(data)
                urls = analysis_data.xpath("//div[@class='g4kCYe']/a/@href")
                return urls
        except:
            try:
                self.proxies.remove(proxy)
            except:
                pass

    def run(self):
        self.apk_names.clear()
        # 获取最外层的apkname
        tasks = self.get_apknames_tasks()

        self.loop.run_until_complete(asyncio.wait(tasks))

        # 获取最外层类别的url，共八种
        urls = self.loop.run_until_complete(self.get_main_url())

        tasks = self.build_async_tasks(urls)

        results = self.loop.run_until_complete(asyncio.gather(*tasks))

        get_data_tasks = []

        # 获取里层的分类的url
        for result in results:
            task = asyncio.ensure_future(self.get_category_url(result))
            get_data_tasks.append(task)

        allurls = self.loop.run_until_complete(asyncio.gather(*get_data_tasks))


        for urls in allurls:
            for url in urls:
                self.son_category_url.add(url)

        get_apkname_tasks = []
        for url in self.son_category_url:
            task = asyncio.ensure_future(self.fetch_get_apkname(url))
            get_apkname_tasks.append(task)

        self.loop.run_until_complete(asyncio.gather(*get_apkname_tasks))

if __name__ == '__main__':
    t = CrawlApkName()
    t.run()