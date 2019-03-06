import asyncio


async def test(number):

    a = {"dada":number}
    b = None

    return a,b


loop = asyncio.get_event_loop()
tasks = []
for i in range(6):
    task = asyncio.ensure_future(test(i))
    tasks.append(task)

results = loop.run_until_complete(asyncio.gather(*tasks))
print(results)
for i in results:
    a,b = i
    print(a)

    print(b)