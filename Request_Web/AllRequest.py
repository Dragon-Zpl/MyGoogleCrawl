

class InitiateRequest:
    def __init__(self):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36",
        }



    async def post_request(self,session,url,proxy,data=None):
        print('post的url:' + str(url))
        async with session.post(url=url, data=data, headers=self.headers, proxy=proxy, timeout=10) as ct:
            print('post的通过url:'+str(url)+str(ct.status))
            if ct.status in [200, 201]:
                data = await ct.text()
                return data
            elif ct.status in [403, 400, 500, 502, 503, 429]:
                pass


    async def get_request(self,session,url,proxy=None):
        print('get的url:'+str(url))
        async with session.get(url=url, headers=self.headers, proxy=proxy, timeout=10) as ct:
            print('get的通过url:'+str(url)+str(ct.status))
            if ct.status in [200,201]:
                data = await ct.text()
                return data
            elif ct.status in [403, 400, 500, 502, 503, 429]:
                return None