
from random import choice
from lxml import etree

import socket
import aiohttp
import redis


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

    async def check_proxy(self,session,proxy_info):
        proxy = 'http://' + str(proxy_info["ip"]) + ':' + str(proxy_info["port"])

        try:
            async with session.get(url="https://google.com", proxy=proxy, headers=self.headers_normal,
                                   timeout=10) as res:
                if res.status == 200:
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
            async with session.get(url=url, headers=headers, timeout=10) as ct:
                if ct.status == 200:
                    code = await ct.text()
                    return code
        except:
            pass

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

class CheckUpdateApkname:
    def __init__(self):
        self.setting = GetSetting()
        self.loop = self.setting.get_loop()
        self.session = self.setting.get_session()
        self.rcon = self.setting.get_redis()
        self.lock = asyncio.Lock()
        self.crawl_proxy = crawl_fn()
        self.apknames = set()
        self.apk_list = []
        self.proxies = []
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36",
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
                if ct.status in [200, 201]:
                    datas = await ct.text()
                    analysis_data = etree.HTML(datas)
                    check_app_version = analysis_data.xpath("//div[@class='hAyfc'][4]//span[@class='htlgb']/text()")[0]
                    if check_app_version == now_app_version:
                        pass
                    else:
                        data_return = {}
                        data_return["app_version"] = check_app_version
                        data_return["pkgname"] = now_pkgname
                        return data_return
                elif ct.status in [403, 400, 500, 502, 503, 429]:
                    if time > 0:
                        print('失败')
                        proxy = await self.get_proxy()
                        return await self.check_app_version(data, proxy=proxy, time=time - 1)
                    else:
                        return None
        except:
            if time > 0:
                proxy = await self.get_proxy()
                return await self.check_app_version(data, proxy=proxy, time=time - 1)
            else:
                return None

    async def save_redis(self, updatedata):
        print('存入数据库'+updatedata["pkgname"])
        data = {}
        data["pkgname"] = updatedata["pkgname"]
        data["app_version"] = updatedata["app_version"]
        data["host"] = "host"
        self.rcon.rpush("download:queen", str(data).encode('utf-8'))

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

                check_results = self.loop.run_until_complete(asyncio.gather(*check_tasks))

                redis_tasks = []

                for check_result in check_results:
                    print(check_result)
                    task = asyncio.ensure_future(self.save_redis(check_result))
                    redis_tasks.append(task)

                self.loop.run_until_complete(asyncio.wait(redis_tasks))


if __name__ == '__main__':
    t = CheckUpdateApkname()
    t.run()