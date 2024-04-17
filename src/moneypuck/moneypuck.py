'''
Script requests and dowloads the data files that are published by MoneyPuck here:
https://moneypuck.com/data.htm
'''

import pandas as pd
import requests
import io
from tqdm import tqdm

def getData(base_url,gametype,file,seasons):
    '''
    Requests and dowloads a specific file from money puck:
    https://moneypuck.com/data.htm

    Args:
        gametype (str): The type of game data to retrieve ('regular' or 'playoff').
        file (str): The name of the data file to retrieve.
        seasons (list): LIst of seasons to pull (ex [2008,2009,2010])

    Returns:
        pandas.DataFrame: The concatenated data frames from the retrieved files.

    Examples:
        >>> getData('regular', 'skaters')
            player_id  season  team_id  ...  goals  assists  points
        0      8470613    2008        1  ...     10       20      30
        1      8470614    2008        2  ...     15       25      40
        ...    ...        ...       ...  ...    ...      ...     ...
        999    8470615    2023       31  ...      5       10      15
    '''
    res = []
    
    for season in tqdm(seasons,desc=f'{gametype} | {file}',ascii=True):
        url = f'{base_url}{season}/{gametype}/{file}.csv'
        r = requests.get(url)
        data = r.content.decode('utf8')
        df = pd.read_csv(io.StringIO(data))
        res.append(df)
    
    return pd.concat(res)

if __name__ == '__main__':
    filenames = ['skaters','goalies','lines','teams']
    seasons = [str(y) for y in range(2008,2024)]
    base_url = 'https://moneypuck.com/moneypuck/playerData/seasonSummary/'

    reg_season = {}
    playoff = {}

    print('Getting regular season data from MoneyPuck.')

    for file in filenames:
        frame = getData(base_url,'regular',file,seasons)
        reg_season[f'fact_{file}Season'] = frame