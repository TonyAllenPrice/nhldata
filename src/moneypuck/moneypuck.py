'''
Script requests and dowloads the data files that are published by MoneyPuck here:
https://moneypuck.com/data.htm

TODO:
Review PageSource and extract URLs
Build functions for each Request type with List[Dict] returns
Helper function for returning file?
'''

import urllib
import csv
import requests
import io

def _url(filetype:str):
    urls = {
        'shots':'https://peter-tanner.com/moneypuck/downloads/',
        'stats':'https://moneypuck.com/moneypuck/playerData/'
    }
    return urls[filetype]

def get_stats(base_url:str,gametype:str,file:str,seasons:list):
    '''
    Requests and dowloads a specific file from MoneyPuck
    Data Dictionary available here: https://peter-tanner.com/moneypuck/downloads/MoneyPuckDataDictionaryForPlayers.csv

    Args:
        gametype (str): The type of game data to retrieve ('regular' or 'playoff').
        file ['skaters','goalies','lines','teams']:The name of the data file to retrieve.
        seasons (list): List of seasons to pull (ex [2008,2009,2010])

    Returns:
        List[Dict]: The concatenated data frames from the retrieved files.
    '''

    res = []

    for season in seasons:
        url = f'{base_url}{season}/{gametype}/{file}.csv'
        r = requests.get(url)
        buff = io.StringIO(r.text)
        a = [dict(row.items()) for row in csv.DictReader(buff, skipinitialspace=True)]
        res.append(a)

    return res

if __name__ == '__main__':
    filenames = ['skaters']
    seasons = [2023]
    base_url = 'https://moneypuck.com/moneypuck/playerData/seasonSummary/'
    'https://moneypuck.com/moneypuck/playerData/careers/gameByGame/regular/teams/COL.csv'

    reg_season = {}
    playoff = {}

    print('Getting regular season data from MoneyPuck.')

    for file in filenames:
        frame = get_stats(base_url,'regular',file,seasons)
        reg_season[f'fact_{file}Season'] = frame