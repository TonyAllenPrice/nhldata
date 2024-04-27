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

def _fetch_file(base:str,endpoint:str,file_name:str):
    url = f'{base}{endpoint}{file_name}.csv'
    r = requests.get(url)
    return io.StringIO(r.text)

def _process_file(base:str,endpoint:str,file_name:str):
    data_stream = _fetch_file(base, endpoint, file_name)
    return [dict(row.items()) for row in csv.DictReader(data_stream, skipinitialspace=True)]

def season_stats(gametype:str,file_type:str,seasons:list):
    res = []  
    for season in seasons:
        endpoint = f'seasonSummary/{season}/{gametype}/'
        res.extend(_process_file(BASE_URL,endpoint,file_type))
    return res

def player_by_game(player_id:int,position:str,gametype:str):
    endpoint = f'careers/gameByGame/{gametype}/{position}/'
    return _process_file(BASE_URL,endpoint,player_id)

def team_stats(gametype:str,team:str):
    endpoint = f'careers/gameByGame/{gametype}/teams/'
    return _process_file(BASE_URL,endpoint,team)

def get_shots(season:int):
    r = requests.get(f'https://peter-tanner.com/moneypuck/downloads/shots_{season}.zip')
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        for zipfile in z.infolist():
            with z.open(zipfile) as thefile:
                yield zipfile.filename, thefile

if __name__ == '__main__':
    shots_2023 = get_shots(2023)
    print(iter(shots_2023))