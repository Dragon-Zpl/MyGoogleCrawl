import socket

import aiohttp
import asyncio

from lxml import etree

url  =  "https://play.google.com/store/apps/collection/topselling_paid?authuser=0"
conn = aiohttp.TCPConnector(family=socket.AF_INET,
                            verify_ssl=False,
                            use_dns_cache=True
                            )
session = aiohttp.ClientSession(connector=conn)
async def test():
    async with session.post(url=url,proxy="http://5.160.150.210:8080",data={'start': 120, 'num': '60', 'numChildren': '0', 'cctcss': 'square-cover', 'cllayout': 'NORMAL', 'ipf': '1', 'xhr': '1'}) as ct:
        data = ct.text()
        analysis_data = etree.HTML(data)
        apknames = analysis_data.xpath(
            "//div[@class='card no-rationale square-cover apps small']//span[@class='preview-overlay-container']/@data-docid")
        for apkname in apknames:
            print(apkname)


loop = asyncio.get_event_loop()

loop.run_until_complete(test())