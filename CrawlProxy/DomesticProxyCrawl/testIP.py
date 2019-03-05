import requests
from lxml import etree
url = 'https://play.google.com/store/apps/details?id=com.ollix.fogofworld'
headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36",
        }
response = requests.get(url=url,headers=headers)
data = response.text
analysis_dic = {}
analysis_data = etree.HTML(data)
xpath_list = analysis_data.xpath("//div[@class='hAyfc']")
print(xpath_list)
print('******')
print('test' + str(xpath_list[0].xpath("./div/text()")))
for xpath_one in xpath_list:
    print('进入循环' + str(xpath_one))
    needxpath = xpath_one.xpath(".//div[contains(@class,'BgcNfc')]")[0]
    print('解析到的：' + str(needxpath.xpath("./text()")[0]))
    print('最终要获取的'+ str(xpath_one.xpath(".//span[@class='htlgb']/text()")))
    if needxpath.xpath("./text()")[0] in ["更新日期", "업데이트 날짜", "تم التحديث", "更新日", "Updated"]:
        print('进入更新日期')
        print(xpath_one.xpath(".//span[@class='htlgb']/text()"))
        analysis_dic["update_time"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
    elif needxpath.xpath("./text()")[0] in ["大小", "크기", "الحجم", "サイズ", "Size"]:
        print('进入尺寸')
        analysis_dic["size"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
    elif needxpath.xpath("./text()")[0] in ["当前版本", "현재 버전", "الإصدار الحالي", "現在のバージョン", "Current Version"]:
        print('进入当前版本')
        analysis_dic["app_version"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
    elif needxpath.xpath("./text()")[0] in ["开发者", "제공", "تقديم", "提供元", "Offered By"]:
        print('进入开发者')
        analysis_dic["provider"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
if analysis_data.xpath("//span[@class='oocvOe']/button/@aria-label")[0] in ["安装", "설치", "تثبيت", "インストール"]:
    analysis_dic["is_busy"] = 0
else:
    analysis_dic["is_busy"] = 1
analysis_dic["name"] = analysis_data.xpath("//h1[@class='AHFaub']/span/text()")
print(analysis_dic)