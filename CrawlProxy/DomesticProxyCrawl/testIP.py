

import requests

from lxml import etree
headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36'
}
response = requests.get('https://www.baidu.com/',headers=headers)

content = response.text
# print(content)
l = etree.HTML(content)

l1 = l.xpath("//div[@class='s_tab_inner']/a")
print(l1)

