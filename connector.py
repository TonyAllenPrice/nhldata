import requests

STATS_URL = "https://api.nhle.com/stats/rest"
WEB_URL = "https://api-web.nhle.com"

class Wrapper:
    def __init__(self, ssl_verify: bool = True):
        self._ssl_verify = ssl_verify
        if not ssl_verify:
            requests.packages.urllib3.disable_warnings()
    
    def _url_check(self, type: str) -> Str:
        #write execrption
        if type == 'stats':
            return STATS_URL
        elif type == 'web':
            return WEB_URL
    
    def get(self, type: str, endpoint: str) -> List[Dict]:
        