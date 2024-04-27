'''
Script requests and dowloads the data files that are published by MoneyPuck here:
https://moneypuck.com/data.htm

Data Dictionary available here: 
https://peter-tanner.com/moneypuck/downloads/MoneyPuckDataDictionaryForPlayers.csv

TODO:
Review PageSource and extract URLs
Build functions for each Request type with List[Dict] returns
'''

import csv
import requests
import io
import zipfile

BASE_URL = 'https://moneypuck.com/moneypuck/playerData/'

def _fetch_and_process_data(base:str, endpoint:str, file_name:str):
    url = f'{base}{endpoint}{file_name}.csv'
    r = requests.get(url)
    data_stream = io.StringIO(r.text)
    return [dict(row.items()) for row in csv.DictReader(data_stream, skipinitialspace=True)]

def season_stats(gametype:str, file_type:str, seasons:list):
    return [data for season in seasons for data in _fetch_and_process_data(BASE_URL, f'seasonSummary/{season}/{gametype}/', file_type)]

def player_by_game(player_id:int, position:str, gametype:str):
    return _fetch_and_process_data(BASE_URL, f'careers/gameByGame/{gametype}/{position}/', player_id)

def team_stats(gametype:str, team:str):
    return _fetch_and_process_data(BASE_URL, f'careers/gameByGame/{gametype}/teams/', team)

def get_shots(season:int):
    r = requests.get(f'https://peter-tanner.com/moneypuck/downloads/shots_{season}.zip')
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        for zip_info in z.infolist():
            with z.open(zip_info) as thefile:
                yield zip_info.filename, thefile

if __name__ == '__main__':
    shots_2023 = get_shots(2023)
    print(iter(shots_2023))