import requests

from Parsing import ParsingData

headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36",
        }
response = requests.get('https://play.google.com/store/apps/details?id=jp.co.dkkaraoke.SPKDAM&hl=en&gl=us',headers=headers)

t = ParsingData()

print(t.analysis_country_data(response.text))