import asyncio

async def test():
    return 'dasdas'



loop = asyncio.get_event_loop()

a = loop.run_until_complete(test())

print(a)