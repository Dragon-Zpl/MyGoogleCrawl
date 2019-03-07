
import requests
from lxml import etree
url = 'https://play.google.com/store/apps/details?id=com.psslabs.rhythmpaid&hl=zh&gl=us'


def analysis_web_data(data):
    analysis_dic = {}
    analysis_data = etree.HTML(data)
    xpath_list = analysis_data.xpath("//div[@class='hAyfc']")
    for xpath_one in xpath_list:
        needxpath = xpath_one.xpath(".//div[contains(@class,'BgcNfc')]")[0]
        print(needxpath.xpath("./text()")[0])
        if needxpath.xpath("./text()")[0] in ["更新日期", "업데이트 날짜", "تم التحديث", "更新日", "Updated"]:
            analysis_dic["update_time"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
        elif needxpath.xpath("./text()")[0] in ["大小", "크기", "الحجم", "サイズ", "Size"]:
            analysis_dic["size"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
        elif needxpath.xpath("./text()")[0] in ["当前版本", "현재 버전", "الإصدار الحالي", "現在のバージョン", "Current Version"]:
            analysis_dic["app_version"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
        elif needxpath.xpath("./text()")[0] in ["提供者", "제공", "تقديم", "提供元", "Offered By"]:
            analysis_dic["provider"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
            # analysis_dic["provider"] = self.remove_emoji(analysis_dic["provider"])
            # analysis_dic["provider"] = self.filter_emoji(analysis_dic["provider"])
        elif needxpath.xpath("./text()")[0] in ["콘텐츠 등급", "تقييم المحتوى", "コンテンツのレーティング", "Content Rating", "內容分級",
                                                "内容分级"]:
            analysis_dic["content_rating"] = xpath_one.xpath(".//span[@class='htlgb']/div/text()")[0]
        elif needxpath.xpath("./text()")[0] in ["개발자", "مطوّر البرامج", "開発元", "Developer", "開發人員", "开发者"]:
            analysis_dic["developer_email"] = xpath_one.xpath(".//a[@class='hrTbp KyaTEc']/text()")[0]
        elif needxpath.xpath("./text()")[0] in ["설치 수", "عمليات التثبيت", "インストール", "Installs", "安裝次數", "安装次数"]:
            analysis_dic["installs"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
        elif needxpath.xpath("./text()")[0] in ["필요한 Android 버전", "يتطلب Android", "Android 要件", "Requires Android",
                                                "Android 系统版本要求", "Android 最低版本需求"]:
            analysis_dic["min_os_version"] = xpath_one.xpath(".//span[@class='htlgb']/text()")[0]
    if analysis_data.xpath("//span[@class='oocvOe']/button/@aria-label")[0] in ["安装", "설치", "تثبيت", "インストール",
                                                                                "Install"]:
        analysis_dic["is_busy"] = 0
    else:
        analysis_dic["is_busy"] = 1
    analysis_dic["name"] = analysis_data.xpath("//h1[@class='AHFaub']/span/text()")[0]
    # analysis_dic["name"] = self.remove_emoji(analysis_dic["name"])
    # analysis_dic["name"] = self.filter_emoji(analysis_dic["name"])
    analysis_dic["developer_url"] = analysis_data.xpath("//a[@class='hrTbp R8zArc']/@href")[0]
    analysis_dic["category"] = analysis_data.xpath("//a[@itemprop='genre']/text()")[0]
    analysis_dic["app_current_num"] = analysis_data.xpath("//span[@class='AYi5wd TBRnV']/span/text()")[0]
    analysis_dic["cover_image_url"] = analysis_data.xpath("//div[@class='dQrBL']/img/@src")[0]
    analysis_dic["description"] = analysis_data.xpath("//meta[@name='description']/@content")[0]
    # analysis_dic["description"] = self.remove_emoji(analysis_dic["description"])
    # analysis_dic["description"] = self.filter_emoji(analysis_dic["description"])
    analysis_dic["what_news"] = ','.join(analysis_data.xpath("//div[@class='DWPxHb']/content/text()"))
    # analysis_dic["what_news"] = self.remove_emoji(analysis_dic["what_news"])
    # analysis_dic["what_news"] = self.filter_emoji(analysis_dic["what_news"])
    return analysis_dic

response = requests.get(url=url)

data = response.text
print(analysis_web_data(data))