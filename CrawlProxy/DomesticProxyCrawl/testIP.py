import re
from datetime import datetime

LastUpdateDate ='2018年7月23日'
lang = 'zh'
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

print(LastUpdateDate)