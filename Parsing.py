import re
from datetime import datetime

from lxml import etree

class ParsingData:
    def __init__(self):
        self._emoji_pattern = re.compile(
        u"(\ud83d[\ude00-\ude4f])|"  # emoticons
        u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
        u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
        u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
        u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
        "+", flags=re.UNICODE)

    def _remove_emoji(self, text):
        return self._emoji_pattern.sub(r'', text)

    # 双重过滤
    def _filter_emoji(self, text):
        '''''
        过滤表情
        '''
        try:
            co = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        return co.sub(r'', text)


    def analysis_country_data(self, data):
        """
        解析传来的数据，解析方法:先抓父节点,在以父节点的文本信息,抓取子节点(防止标签位置改变)

        """
        analysis_dic = {'update_time': '', 'size': '', 'installs': '', 'app_version': '', 'min_os_version': '',
                        'content_rating': '', 'provider': '', 'developer_email': '', 'is_busy': '', 'name': '',
                        'developer_url': '', 'category': '', 'app_current_num': '', 'cover_image_url': '',
                        'description': '', 'what_news': '', 'country': ''}
        analysis_data = etree.HTML(data)
        xpath_list = analysis_data.xpath("//div[@class='hAyfc']")
        for xpath_one in xpath_list:
            needxpath = self._is_existence(xpath_one.xpath(".//div[contains(@class,'BgcNfc')]"))
            if needxpath.xpath("./text()")[0] in ["更新日期", "업데이트 날짜", "تم التحديث", "更新日", "Updated"]:
                analysis_dic["update_time"] = self._is_existence(xpath_one.xpath(".//span[@class='htlgb']/text()"))
            elif needxpath.xpath("./text()")[0] in ["大小", "크기", "الحجم", "サイズ", "Size"]:
                analysis_dic["size"] = self._is_existence(xpath_one.xpath(".//span[@class='htlgb']/text()"))
            elif needxpath.xpath("./text()")[0] in ["当前版本", "目前版本", "현재 버전", "الإصدار الحالي", "現在のバージョン",
                                                    "Current Version"]:
                analysis_dic["app_version"] = self._is_existence(xpath_one.xpath(".//span[@class='htlgb']/text()"))
            elif needxpath.xpath("./text()")[0] in ["提供者：", "제공", "تقديم", "提供元", "Offered By"]:
                analysis_dic["provider"] = self._is_existence(xpath_one.xpath(".//span[@class='htlgb']/text()"))
                analysis_dic["provider"] = self._remove_emoji(analysis_dic["provider"])
                analysis_dic["provider"] = self._filter_emoji(analysis_dic["provider"])
            elif needxpath.xpath("./text()")[0] in ["콘텐츠 등급", "تقييم المحتوى", "コンテンツのレーティング", "Content Rating",
                                                    "內容分級",
                                                    "内容分级"]:
                analysis_dic["content_rating"] = self._is_existence(xpath_one.xpath(".//span[@class='htlgb']/div/text()"))
            elif needxpath.xpath("./text()")[0] in ["개발자", "مطوّر البرامج", "開発元", "Developer", "開發人員", "开发者"]:
                analysis_dic["developer_email"] = self._is_existence(xpath_one.xpath(".//a[@class='hrTbp KyaTEc']/text()"))
            elif needxpath.xpath("./text()")[0] in ["설치 수", "عمليات التثبيت", "インストール", "Installs", "安裝次數", "安装次数"]:
                analysis_dic["installs"] = self._is_existence(xpath_one.xpath(".//span[@class='htlgb']/text()"))
            elif needxpath.xpath("./text()")[0] in ["필요한 Android 버전", "يتطلب Android", "Android 要件",
                                                    "Requires Android",
                                                    "Android 系统版本要求", "Android 最低版本需求"]:
                analysis_dic["min_os_version"] = self._is_existence(xpath_one.xpath(".//span[@class='htlgb']/text()"))
        is_busy = analysis_data.xpath("//span[@class='oocvOe']/button/@aria-label")
        if is_busy:
            if analysis_data.xpath("//span[@class='oocvOe']/button/@aria-label")[0] in ["安装", "설치", "تثبيت",
                                                                                        "インストール",
                                                                                        "Install"]:
                analysis_dic["is_busy"] = 0
            else:
                analysis_dic["is_busy"] = 1
        else:
            return None
        analysis_dic["name"] = self._is_existence(analysis_data.xpath("//h1[@class='AHFaub']/span/text()"))
        analysis_dic["name"] = self._remove_emoji(analysis_dic["name"])
        analysis_dic["name"] = self._filter_emoji(analysis_dic["name"])
        analysis_dic["developer_url"] = self._is_existence(analysis_data.xpath("//a[@class='hrTbp R8zArc']/@href"))
        analysis_dic["category"] = self._is_existence(analysis_data.xpath("//a[@itemprop='genre']/text()"))
        analysis_dic["app_current_num"] = self._is_existence(
            analysis_data.xpath("//span[@class='AYi5wd TBRnV']/span/text()"))
        analysis_dic["cover_image_url"] = self._is_existence(analysis_data.xpath("//div[@class='dQrBL']/img/@src"))
        analysis_dic["description"] = self._is_existence(
            analysis_data.xpath("//meta[@name='description']/@content"))
        analysis_dic["description"] = self._remove_emoji(analysis_dic["description"])
        analysis_dic["description"] = self._filter_emoji(analysis_dic["description"])
        what_news = analysis_data.xpath("//div[@class='DWPxHb']/content/text()")
        if what_news:
            analysis_dic["what_news"] = ','.join(what_news)
            analysis_dic["what_news"] = self._remove_emoji(analysis_dic["what_news"])
            analysis_dic["what_news"] = self._filter_emoji(analysis_dic["what_news"])
        return analysis_dic


    def _is_existence(self, data):
        """
        判断该数据是否存在
        """
        if data:
            return data[0]
        else:
            return ""

    def change_time(self, lang, LastUpdateDate):
        '''
        将各个国家的时间更改为可存入数据库的时间(阿拉伯的有问题无法更改)
        '''
        if LastUpdateDate:
            if lang == 'us':
                try:
                    LastUpdateDate = datetime.strptime(LastUpdateDate, '%B %d, %Y')
                except:
                    LastUpdateDate = re.findall('([0-9/])', LastUpdateDate)
                    LastUpdateDate = ''.join(LastUpdateDate)
                    LastUpdateDate = datetime.strptime(LastUpdateDate, '%m/%d/%Y')
            elif lang == 'ko':
                LastUpdateDate = datetime.strptime(LastUpdateDate, '%Y년 %m월 %d일')
            elif lang == 'ar':
                # arabic date need to be process specially
                LastUpdateDate = "2019-01-01 00:00:00"
            else:
                try:
                    LastUpdateDate = datetime.strptime(LastUpdateDate, '%Y年%m月%d日')
                except:
                    LastUpdateDate = "2019-01-01 00:00:00"
            return str(LastUpdateDate)