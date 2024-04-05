'''
Fetches the rosters for all active teams for the last n seasons.

Handles expansion teams by getting all seasons if before the first season desired (defaults to 2008/2009)
'''

import requests
import pandas as pd
import itertools
from sqlalchemy import create_engine

def getSeasons():
    '''
    Returns the seasons available in the NHL API.

    Returns:
        dict: A dictionary containing the seasons available in the NHL API.

    Examples:
        >>> getSeasons()
        {
            'seasons': [
                {'seasonId': '20202021', 'regularSeasonStartDate': '2021-01-13', 'regularSeasonEndDate': '2021-05-08', 'seasonEndDate': '2021-07-09', 'numberOfGames': 868},
                {'seasonId': '20192020', 'regularSeasonStartDate': '2019-10-02', 'regularSeasonEndDate': '2020-04-04', 'seasonEndDate': '2020-09-28', 'numberOfGames': 1271},
                ...
            ]
        }
    '''

    base = f"{web_url}/v1/season"
    response = requests.get(base)
    return response.json()
    
def getActiveTeams(season):
    '''
    Returns a list of active NHL teams for a given season.

    Args:
        season (str): The season for which to retrieve the active teams.

    Returns:
        list: A list of three-letter team abbreviations representing the active NHL teams for the given season.

    Examples:
        >>> getActiveTeams('20202021')
        ['NYR', 'BOS', 'TOR', 'MTL', 'VAN', 'EDM', 'CHI', 'MIN', '...', 'LAK']
    '''

    base = f"{stats_url}/en/goalie/summary?limit=-1&sort=wins&cayenneExp=seasonId={season}"
    response = requests.get(base)
    data = response.json()
    goalies = data['data']
    teams = [g['teamAbbrevs'] for g in goalies]
    teams = list(set(teams))
    return [t for t in teams if len(t) == 3]

def getTeamSeasons(team):
    '''
    Returns the seasons in which a specific NHL team has played.

    Args:
        team (str): The team abbreviation for which to retrieve the seasons.

    Returns:
        dict: A dictionary containing the seasons in which the specified team played.

    Examples:
        >>> getTeamSeasons('NYR')
        {
            'teamId': 3,
            'abbreviation': 'NYR',
            'teamName': 'New York Rangers',
            'rosterSeasons': [
                {'seasonId': '20202021', 'regularSeasonStartDate': '2021-01-13', 'regularSeasonEndDate': '2021-05-08', 'seasonEndDate': '2021-07-09', 'numberOfGames': 56},
                {'seasonId': '20192020', 'regularSeasonStartDate': '2019-10-02', 'regularSeasonEndDate': '2020-04-04', 'seasonEndDate': '2020-09-28', 'numberOfGames': 70},
                ...
            ]
        }
    '''

    base = f'{web_url}/v1/roster-season/{team}'
    response = requests.get(base)
    return response.json()

def getTeams():
    '''
    Returns a DataFrame containing information about NHL teams.

    Returns:
        pandas.DataFrame: A DataFrame containing information about NHL teams, including team IDs, abbreviations, names, and other details.

    Examples:
        >>> getTeams()
        teamId abbreviation       teamName  ...  venueTimezone  venueCity  venueTimeZoneOffset
        0       1          NJD  New Jersey ...  ...            EDT  Newark     -4
        1       2          NYI  New York ...   ...            EDT  Uniondale  -4
        ...
    '''
    base = f"{stats_url}/en/team"
    response = requests.get(base)
    data = response.json()
    return pd.DataFrame(data['data'])

def getTeamName(team):
    '''
    Returns the full name of an NHL team given its abbreviation.

    Args:
        team (str): The team abbreviation for which to retrieve the full name.

    Returns:
        str: The full name of the NHL team.

    Examples:
        >>> getTeamName('NYR')
        'New York Rangers'
    '''

    return teams_df.loc[teams_df['triCode'] == team, 'fullName'].iloc[0]

def getRoster(team,season):
    '''
    Returns a DataFrame containing the roster of an NHL team for a specific season.

    Args:
        team (str): The team abbreviation for which to retrieve the roster.
        season (str): The season for which to retrieve the roster.

    Returns:
        pandas.DataFrame: A DataFrame containing the roster of the specified NHL team for the given season, including player information such as first name, last name, birth city, and birth state/province.

    Examples:
        >>> getRoster('NYR', '20202021')
            personId  jerseyNumber  ...  birthCity  birthStateProvince
        0    8478402            20  ...  St. Paul   MN
        1    8478403            21  ...  Regina     SK
        ...
    '''

    base = f"{web_url}/v1/roster/{team}/{season}"
    response = requests.get(base)
    data = response.json()
    players = [data[pos] for pos in data]
    changes = ['firstName','lastName','birthCity','birthStateProvince'] # These 4 have nested natures with FR translations. We are pulling just English/Default.
    players = list(itertools.chain.from_iterable(players))
    for player, change in itertools.product(players, changes):
        if change in player: # Not every player has a State/Province, but this allows one loop to do all 4 changes.
            player[change] = player[change]['default']
    return pd.DataFrame(players)

def getSkaterStats(totalplayers,season):
    '''
    Returns the skater statistics for a specific season.

    Args:
        totalplayers (int): The total number of skaters for the season.
        season (str): The season for which to retrieve the skater statistics.

    Returns:
        list: A list of dictionaries containing the skater statistics for the specified season.

    Examples:
        >>> getSkaterStats(1000, '20202021')
        [
            {'playerId': 8478402, 'seasonId': '20202021', 'teamId': 3, 'teamAbbrevs': 'NYR', 'goals': 10, 'assists': 20, 'points': 30},
            {'playerId': 8478403, 'seasonId': '20202021', 'teamId': 3, 'teamAbbrevs': 'NYR', 'goals': 15, 'assists': 25, 'points': 40},
            ...
        ]
    '''

    start = 0
    results = []
    while start < totalplayers:
        base = f'{stats_url}/en/skater/summary?limit=100&start={start}&cayenneExp=seasonId={season}'
        response = requests.get(base)
        data = response.json()
        results.append(data['data'])
        start += 100
    
    return list(itertools.chain.from_iterable(results))

def getGoalieStats(totalplayers,season):
    '''
    Returns the goalie statistics for a specific season.

    Args:
        totalplayers (int): The total number of goalies for the season.
        season (str): The season for which to retrieve the goalie statistics.

    Returns:
        list: A list of dictionaries containing the goalie statistics for the specified season.

    Examples:
        >>> getGoalieStats(100, '20202021')
        [
            {'playerId': 8478402, 'seasonId': '20202021', 'teamId': 3, 'teamAbbrevs': 'NYR', 'wins': 20, 'losses': 10, 'savePercentage': 0.92},
            {'playerId': 8478403, 'seasonId': '20202021', 'teamId': 3, 'teamAbbrevs': 'NYR', 'wins': 15, 'losses': 12, 'savePercentage': 0.91},
            ...
        ]
    '''

    start = 0
    results = []
    while start < totalplayers:
        base = f'{stats_url}/en/goalie/summary?limit=100&start={start}&cayenneExp=seasonId={season}'
        response = requests.get(base)
        data = response.json()
        results.append(data['data'])
        start += 100
    
    return list(itertools.chain.from_iterable(results))

if __name__ == '__main__':
    stats_url = "https://api.nhle.com/stats/rest"
    web_url = "https://api-web.nhle.com"

    allseasons = getSeasons()
    teams_df = getTeams()
    activeTeams = getActiveTeams(f'{max(allseasons)}')

    rosters = []

    for team in activeTeams:
        seasons = getTeamSeasons(team)
        seasons = seasons if len(seasons) < 5 else seasons[-25:]
        for season in seasons:
            team_name = getTeamName(team)
            roster_df = getRoster(team,season)
            roster_df['Team'] = team_name
            roster_df['seasonId'] = season
            rosters.append(roster_df)

    rosters_df = pd.concat(rosters)
    rosters_df = rosters_df.reset_index(drop=True)

    engine = create_engine(r"sqlite:///nhldata.db")
    conn = engine.raw_connection()

    rosters_df.to_sql(name='dim_Rosters',con=conn,if_exists='replace')
    conn.commit()
    conn.close()