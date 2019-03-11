import requests

from Parsing import ParsingData

headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36",
        }
response = requests.get('https://play.google.com/store/apps/details?id=com.astragon.cs2016&hl=en&gl=us',headers=headers)

t = ParsingData()

t.analysis_country_data(response.text,'com.astragon.cs2016')