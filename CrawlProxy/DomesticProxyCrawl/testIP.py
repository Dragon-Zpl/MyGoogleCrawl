import asyncio


class Test:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def get_loop(self):

        loop = asyncio.get_running_loop()
        print(loop)
        if loop is None:
            loop = asyncio.get_event_loop()
        return loop


async def test():
    print('dasdas')


t = Test()

loop = t.get_loop()

loop.run_until_complete(test())