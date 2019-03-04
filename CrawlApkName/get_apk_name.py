from AllSetting import GetSetting
from lxml import etree
import asyncio
from random import choice
from CrawlProxy.ForeignProxyCrawl.crawl_foreigh_auto import crawl_fn


class CrawlApkName:
    def __init__(self):
        self.apk_names = set()
        self.son_category_url = set()
        self.session = GetSetting().get_session()
        self.crawl_proxy = crawl_fn()
        self.loop = GetSetting().get_loop()
        self.lock = asyncio.Lock()
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
                    print(apkname)
                    self.apk_names.add(apkname)
        except Exception as e:
            try:
                self.proxies.remove(proxy)
            except:
                pass

    async def fetch_get_apkname(self,url):
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
            if "GAME" in url or "SOCIAL" in url or "SPORTS" in url or "SHOPPING" in url or "HEALTH_AND_FITNESS" in url or "COMICS" in url:
                feasible_url.add(url)
        return feasible_url

    async def get_proxy(self):
        async with self.lock:
            if len(self.proxies) < 3:
                self.proxies = await self.crawl_proxy.run(self.session)
            try:
                proxy = choice(self.proxies)
                return proxy
            except:
                await self.get_proxy()

    async def get_web_data(self, url):
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
        proxy = await self.get_proxy()
        url = "https://play.google.com/store/apps"
        try:
            async with self.session.get(url=url, headers=self.headers, proxy=proxy, timeout=10) as tc:
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


        # 获取里层的分类的url

        task = asyncio.ensure_future(self.get_category_url(results[0]))


        allurls = self.loop.run_until_complete(task)


        for url in allurls:
            self.son_category_url.add(url)

        get_apkname_tasks = []
        for url in self.son_category_url:
            task = asyncio.ensure_future(self.fetch_get_apkname(url))
            get_apkname_tasks.append(task)

        self.loop.run_until_complete(asyncio.gather(*get_apkname_tasks))

if __name__ == '__main__':
    t = CrawlApkName()
    t.run()