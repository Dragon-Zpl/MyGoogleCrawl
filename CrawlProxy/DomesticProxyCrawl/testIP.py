import requests
from lxml import etree
import random
import threading
headers = {
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
}
#
# proxies = {
#             'https': 'https:119.101.117.137:9999'
#         }

ipdict = {}
okip = {}
number = 0
httpnum = 0
def getip():

    proxies = {
        'http': 'http' + '://' + '60.217.64.237:45091'
    }
    for i in range(0,2):
        if i == 0:
            url = 'https://www.xicidaili.com/nn/'
        else:
            url = 'https://www.xicidaili.com/nn/' + str(i)
        response = requests.get(url=url, headers=headers,proxies=proxies)
        print('经过````')
        content = etree.HTML(response.text)

        alltr = content.xpath("//table[@id='ip_list']//tr[@class='odd']")
        for oneip in alltr:
            ip = oneip.xpath(".//td[2]/text()")[0]
            port = oneip.xpath(".//td[3]/text()")[0]
            ips = ip+':'+port
            type = oneip.xpath(".//td[6]/text()")[0]
            ipdict[ips] = type.lower()
def testIP(count):
    global number
    print('子线程https' + str(count) + '开始')
    while number<20:
        ips = random.choice(list(ipdict.keys()))
        type = ipdict[ips]
        while type != 'https':
            ips = random.choice(list(ipdict.keys()))
            type = ipdict[ips]
        proxies = {
            type: type + '://' + ips
        }
        try:
            response = requests.get(url='https://www.xicidaili.com/nn/', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
},proxies=proxies, timeout=3)
            # print(response.status_code)
            if response.status_code == 200 and (ips not in okip.keys()):
                print('线程https' + str(count) + 'success')
                print(ips)
                print(okip.keys())
                okip[ips] = type
                number += 1
        except Exception as e:
            # print('这个不行')
            pass

okhttpip = {}

def testhttpIP(count):
    global httpnum
    print('子线程http' + str(count) + '开始')
    while httpnum<20:
        ips = random.choice(list(ipdict.keys()))
        type = ipdict[ips]
        while type != 'http':
            ips = random.choice(list(ipdict.keys()))
            type = ipdict[ips]
        proxies = {
            type: type + '://' + ips
        }
        try:
            response = requests.get(url='http://music.163.com/api/song/lyric?id=16574216&lv=1&kv=1&tv=-1', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
},proxies=proxies, timeout=3)
            # print(response.status_code)
            if response.status_code == 200 and (ips not in okhttpip.keys()):
                print('线程http' + str(count) + 'success')
                print(ips)
                print(okhttpip.keys())
                okhttpip[ips] = type
                httpnum += 1
        except Exception as e:
            # print('这个不行')
            pass


if __name__ == '__main__':
    print('主线程开始')
    getip()
    print(ipdict)
    thread_list = []
    with open('allip.txt','w') as fp:
        fp.write(str(ipdict))
    for i,j in zip(range(5),range(5)):
        t = threading.Thread(target=testIP,args=(i,))
        t1 = threading.Thread(target=testhttpIP,args=(j,))
        thread_list.append(t)
        thread_list.append(t1)
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()

    with open('okip.txt','w') as fp:
        fp.write(str(okip))
    IPPOOL = []
    for i in okip.keys():
        dic = {}
        dic['ipaddr'] = i
        IPPOOL.append(dic)
    with open('httpsip.txt','w') as fp:
        fp.write(str(IPPOOL))
    IPPOOL = []
    for i in okhttpip.keys():
        dic = {}
        dic['ipaddr'] = i
        IPPOOL.append(dic)
    with open('httpip.txt','w') as fp:
        fp.write(str(IPPOOL))
    print('主线程结束')