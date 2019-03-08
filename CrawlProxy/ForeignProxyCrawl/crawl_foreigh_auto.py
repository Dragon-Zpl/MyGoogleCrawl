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
        print('进来了')
        proxies = []
        results = await self.get_useful_proxy(session)

        for result in results:
            if result != None:
                proxies.append(result)
        print('proxies'+str(proxies))
        return proxies

