import asyncio
import socket

import aiohttp


from lxml import etree

from AllSetting import GetSetting


class CrawlProxy:
    def __init__(self):
        self.headers = {
            'User-Agent':  'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        }

    def build_async_tasks(self, session):
        print('创建任务队列')
        tasks = []
        for page in range(0,1):
            if page == 0:
                url = 'https://www.xicidaili.com/nn/'
            else:
                url = 'https://www.xicidaili.com/nn/' + str(page)
            task = asyncio.ensure_future(self.crawl_web(url, session))
            tasks.append(task)
        return tasks


    async def crawl_web(self,url, session):
        try:
            print('进入爬取解析')
            async with session.get(url=url, headers=self.headers) as ct:
                text = await ct.text()
                content = etree.HTML(text)
                ip_list = content.xpath("//table[@id='ip_list']//tr[@class='odd']")
                all_proxy = []
                for oneip in ip_list:
                    if oneip.xpath(".//td[6]/text()")[0].lower() == 'http':
                        ipdic = {}
                        ipdic["ip"] = oneip.xpath(".//td[2]/text()")[0]
                        ipdic["port"] = oneip.xpath(".//td[3]/text()")[0]
                        ipdic["addr"] = ''.join(oneip.xpath(".//td[4]//text()"))
                        ipdic["hide"] = oneip.xpath(".//td[5]/text()")[0]
                        ipdic["type"] = oneip.xpath(".//td[6]/text()")[0].lower()
                        ipdic["savetime"] = oneip.xpath(".//td[9]/text()")[0]
                        ipdic["updatetime"] = oneip.xpath(".//td[10]/text()")[0]
                        all_proxy.append(ipdic)
                return all_proxy
        except Exception as e:
            pass

    async def check_proxy(self, ipdic, session):
        print('检查代理')
        proxy = 'http://' + ipdic["ip"] + ":" + ipdic["port"]
        try:
            async with session.get(url='https://play.google.com/store', headers=self.headers, proxy=proxy, timeout=10) as ct:
                if ct.status in [200,201]:
                    print(ct.status)
                    return proxy
        except Exception as e:
            pass

    async def save_mysql(self, ipdic):
        print('存入数据库')
        print(ipdic)

    def run(self):
        proxies = []
        setting = GetSetting()
        session = setting.get_session()
        loop = setting.get_loop()
        tasks = await self.build_async_tasks(session)
        check_tasks = []
        for proxy in tasks:
            for ipdic in proxy.result():
                task = asyncio.ensure_future(self.check_proxy(ipdic,session))
                check_tasks.append(task)
        loop.run_until_complete(asyncio.wait(check_tasks))
        if check_tasks:
            mysql_tasks = []
            for proxy in check_tasks:
                if proxy.result():
                    task = asyncio.ensure_future(self.save_mysql(proxy.result()))
                    mysql_tasks.append(task)
                    proxies.append(proxy.result())
            loop.run_until_complete(asyncio.wait(mysql_tasks))
        return proxies



if __name__ == '__main__':
    t = CrawlProxy()
    t.run()