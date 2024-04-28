import requests
from typing import List, Dict

class Wrapper:
    def __init__(self, ver:str = 'v1', lang:str = 'en', ssl_verify: bool = True):
        """
        Initializes the Wrapper object.

        Args:
            ver (str, optional): The version of the API. Defaults to 'v1'.
            lang (str, optional): The language for the API response. Defaults to 'en'.
            ssl_verify (bool, optional): Whether to verify SSL certificates. Defaults to True.

        Returns:
            None.

        Raises:
            None.
        """
        self._ver = ver
        self._lang = lang
        self._ssl_verify = ssl_verify
        if not ssl_verify:
            requests.packages.urllib3.disable_warnings()

    def _url_check(self, type: str) -> str:
        """
        Check the URL based on the type of data.

        Args:
            type (str): The type of data.

        Returns:
            str: The corresponding URL based on the type.

        Raises:
            None.
        """
        url_mapping = {
            'stats': f"https://api.nhle.com/stats/rest/{self._lang}",
            'web': f"https://api-web.nhle.com/{self._ver}"
        }
        return url_mapping.get(type, "")

    def get(self, type:str, endpoint:str, ep_params:dict = None) -> List[Dict]:
        """
        Send a GET request to the NHL API and retrieve data.

        Args:
            type (str): The type of data to retrieve.
            endpoint (str): The endpoint to retrieve data from.
            ep_params (dict, optional): Additional parameters for the endpoint. Defaults to None.

        Returns:
            List[Dict]: The data retrieved from the NHL API.

        Raises:
            NHLApiException: If the request to the API fails.

        Examples:
            >>> get('web', 'players', {'team': 'NYR'})
            [{'id': 1, 'name': 'John Doe'}, {'id': 2, 'name': 'Jane Smith'}]
        """
        base_url = self._url_check(type)
        full_url = f'{base_url}/{endpoint}'
        response = requests.get(url=full_url, params=ep_params, verify=self._ssl_verify)
        response.raise_for_status()
        return response.json()
