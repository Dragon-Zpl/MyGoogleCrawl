

class InitiateRequest:
    def __init__(self):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36",
        }



    async def post_request(self,session,url,proxy,data=None):
        async with session.post(url=url, data=data, headers=self.headers, proxy=proxy, timeout=10) as ct:
            data = await ct.text()
            return data


    async def get_request(self,session,url,proxy):
        async with session.get(url=url, headers=self.headers, proxy=proxy, timeout=10) as ct:
            data = ct.text()
            return data