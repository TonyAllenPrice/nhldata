import requests
from typing import List, Dict
from exceptions import NHLApiException

class Wrapper:
    def __init__(self, ver:str = 'v1', lang:str = 'en', ssl_verify: bool = True):
        self._ver = ver
        self._lang = lang
        self._ssl_verify = ssl_verify
        if not ssl_verify:
            requests.packages.urllib3.disable_warnings()
    
    def _url_check(self, type: str) -> str:
        #write execrption       
        if type == 'stats':
            stats_url = "https://api.nhle.com/stats/rest/"
            return f'{stats_url}{self._lang}'
        elif type == 'web':
            web_url = "https://api-web.nhle.com/"
            return f'{web_url}{self._ver}'
    
    def get(self, type:str, endpoint:str, ep_params:dict = None) -> List[Dict]:
        base_url = self._url_check(type)
        full_url = f'{base_url}/{endpoint}'
        print(full_url)
        try:
            response = requests.get(url=full_url, params=ep_params)
        except requests.exceptions.RequestException as e:
            raise NHLApiException("Request failed") from e
        data_out = response.json()
        if 299 >= response.status_code >= 200:
            return data_out
    