'''
Master version of NHL API functions. Working on building complete NHL API package for Python.
'''

import requests
import itertools

STATS_URL = "https://api.nhle.com/stats/rest"
WEB_URL = "https://api-web.nhle.com"

def seasons():
    '''
    Access the seasons endpoint of the NHL API.

    Returns:
        list: A list containing the seasons available in the NHL API.

    Examples:
        >>> getSeasons()
        [19171918, 19181919, 19191920, ... 20212022, 20222023, 20232024]
    '''

    base = f"{WEB_URL}/v1/season"
    response = requests.get(base)
    return response.json()
    
def active_teams(season):
    '''
    Leverages the goaies endpoint to create a list of currently active NHL teams.

    Args:
        season (str): The season for which to retrieve the active teams.

    Returns:
        list: A list of three-letter team abbreviations representing the active NHL teams for the given season.

    Examples:
        >>> getActiveTeams('20202021')
        ['NYR', 'BOS', 'TOR', 'MTL', 'VAN', 'EDM', 'CHI', 'MIN', ... 'LAK']
    '''

    base = f"{STATS_URL}/en/goalie/summary"
    payload = {
                'limit':'-1',
                'cayenneExp':'',
                'seasonId':season
            }
    response = requests.get(base,params=payload)
    data = response.json()
    goalies = data['data']
    teams = [g['teamAbbrevs'] for g in goalies]
    teams = list(set(teams))
    return [t for t in teams if len(t) == 3]

def team_seasons(team):
    '''
    Accesses the roster season endpoint of the NHL API.

    Args:
        team (str): The team abbreviation for which to retrieve the seasons.

    Returns:
        list: A list containing the seasons in which the specified team played.

    Examples:
        >>> getTeamSeasons('TOR')
        [
            [19261927, 19271928, 19281929, ... 20212022, 20222023, 20232024]
        ]
    '''

    base = f'{WEB_URL}/v1/roster-season/{team}'
    response = requests.get(base)
    return response.json()

def teams():
    '''
    Accesses the teams endpoint of the NHL API.

    Returns:
        list[dict]: A list of dictionaries containing information about NHL teams, including team IDs, abbreviations, names, and other details.

    Examples:
        >>> teams()
        [
            {'id': 11, 'franchiseId': 35, 'fullName': 'Atlanta Thrashers', 'leagueId': 133, 'rawTricode': 'ATL', 'triCode': 'ATL'}, 
            {'id': 34, 'franchiseId': 26, 'fullName': 'Hartford Whalers', 'leagueId': 133, 'rawTricode': 'HFD', 'triCode': 'HFD'}
            ...
        ]
    '''
    base = f"{STATS_URL}/en/team"
    response = requests.get(base)
    data = response.json()
    return data['data']

def roster(team,season):
    '''
    Returns a DataFrame containing the roster of an NHL team for a specific season.

    Args:
        team (str): The team abbreviation for which to retrieve the roster.
        season (str): The season for which to retrieve the roster.

    Returns:
        list[dict]: A list of dictionaries containing the roster of the specified NHL team for the given season, including player information such as first name, last name, birth city, and birth state/province.

    Examples:
        >>> roster('COL', '20232024')
        [
            {'id': 8471699, 'headshot': 'https://assets.nhle.com/mugs/nhl/20232024/COL/8471699.png', 'firstName': 'Andrew', 'lastName': 'Cogliano', 'sweaterNumber': 11, 'positionCode': 'C', 'shootsCatches': 'L', 'heightInInches': 70, 'weightInPounds': 179, 'heightInCentimeters': 178, 'weightInKilograms': 81, 'birthDate': '1987-06-14', 'birthCity': 'Toronto', 'birthCountry': 'CAN', 'birthStateProvince': 'Ontario'}, 
            {'id': 8479525, 'headshot': 'https://assets.nhle.com/mugs/nhl/20232024/COL/8479525.png', 'firstName': 'Ross', 'lastName': 'Colton', 'sweaterNumber': 20, 'positionCode': 'C', 'shootsCatches': 'L', 'heightInInches': 72, 'weightInPounds': 194, 'heightInCentimeters': 183, 'weightInKilograms': 88, 'birthDate': '1996-09-11', 'birthCity': 'Robbinsville', 'birthCountry': 'USA', 'birthStateProvince': 'New Jersey'},
            ...
        ]
    '''

    base = f"{WEB_URL}/v1/roster/{team}/{season}"
    response = requests.get(base)
    data = response.json()
    players = [data[pos] for pos in data]
    changes = ['firstName','lastName','birthCity','birthStateProvince'] # These 4 have nested natures with FR translations. We are pulling just English/Default.
    players = list(itertools.chain.from_iterable(players))
    for player, change in itertools.product(players, changes):
        if change in player: # Not every player has a State/Province, but this allows one loop to do all 4 changes.
            player[change] = player[change]['default']
    return players

def skater_stats(total_players,season):
    '''
    Returns the skater statistics for a specific season.

    Args:
        totalplayers (int): The total number of skaters for the season.
        season (str): The season for which to retrieve the skater statistics.

    Returns:
        list: A list of dictionaries containing the skater statistics for the specified season.

    Examples:
        >>> skater_stats(1000, '20202021')
        [
            {'playerId': 8478402, 'seasonId': '20202021', 'teamId': 3, 'teamAbbrevs': 'NYR', 'goals': 10, 'assists': 20, 'points': 30},
            {'playerId': 8478403, 'seasonId': '20202021', 'teamId': 3, 'teamAbbrevs': 'NYR', 'goals': 15, 'assists': 25, 'points': 40},
            ...
        ]
    '''

    start = 0
    results = []
    while start < total_players:
        base = f'{STATS_URL}/en/skater/summary'
        payload = {
                'limit':'100',
                'start':start,
                'cayenneExp':'',
                'seasonId':season
            }
        response = requests.get(base,params=payload)
        data = response.json()
        results.append(data['data'])
        start += 100
    
    return list(itertools.chain.from_iterable(results))

def goalies_stats(total_players,season):
    '''
    Returns the goalie statistics for a specific season.

    Args:
        totalplayers (int): The total number of goalies for the season.
        season (str): The season for which to retrieve the goalie statistics.

    Returns:
        list: A list of dictionaries containing the goalie statistics for the specified season.

    Examples:
        >>> goalie_stats(100, '20202021')
        [
            {'playerId': 8478402, 'seasonId': '20202021', 'teamId': 3, 'teamAbbrevs': 'NYR', 'wins': 20, 'losses': 10, 'savePercentage': 0.92},
            {'playerId': 8478403, 'seasonId': '20202021', 'teamId': 3, 'teamAbbrevs': 'NYR', 'wins': 15, 'losses': 12, 'savePercentage': 0.91},
            ...
        ]
    '''

    start = 0
    results = []
    while start < total_players:
        base = f'{STATS_URL}/en/goalie/summary'
        payload = {
                'limit':'100',
                'start':start,
                'cayenneExp':'',
                'seasonId':season
            }
        response = requests.get(base,params=payload)
        data = response.json()
        results.append(data['data'])
        start += 100
    
    return list(itertools.chain.from_iterable(results))

def player_game_log(player_id,season,game_type):
    '''
    Access the gamelog endpoint of the NHL API. ONly contains completed games.

    Args:
        playerId (int): The numeric player ID
        season (int): The season in YYYYYYYY format
        game_type (int): Regular Season (2) or Playoffs (3)

    Returns:
        list[dict]: List of dictionaries containing player specific stats by game for all games in a season.

    Examples:
    >>> player_game_log(8478402,20232024,2)
    [
        {'gameId': 2023021226, 'teamAbbrev': 'EDM', 'homeRoadFlag': 'R', 'gameDate': '2024-04-06', 'goals': 0, 'assists': 2, 'commonName': {'default': 'Oilers'}, 'opponentCommonName': {'default': 'Flames'}, 'points': 2, 'plusMinus': 0, 'powerPlayGoals': 0, 'powerPlayPoints': 2, 'gameWinningGoals': 0, 'otGoals': 0, 'shots': 3, 'shifts': 22, 'shorthandedGoals': 0, 'shorthandedPoints': 0, 'opponentAbbrev': 'CGY', 'pim': 0, 'toi': '20:39'}, 
        {'gameId': 2023021214, 'teamAbbrev': 'EDM', 'homeRoadFlag': 'H', 'gameDate': '2024-04-05', 'goals': 2, 'assists': 0, 'commonName': {'default': 'Oilers'}, 'opponentCommonName': {'default': 'Avalanche'}, 'points': 2, 'plusMinus': 2, 'powerPlayGoals': 0, 'powerPlayPoints': 0, 'gameWinningGoals': 0, 'otGoals': 0, 'shots': 9, 'shifts': 18, 'shorthandedGoals': 0, 'shorthandedPoints': 0, 'opponentAbbrev': 'COL', 'pim': 0, 'toi': '20:11'},
        ...
    ]
    '''

    base = f'{WEB_URL}/v1/player/{player_id}/game-log/{season}/{game_type}'
    response = requests.get(base)
    data = response.json()
    return data['gameLog']

def player_info(player_id):
    '''
    Retrieve player information from the API.

    Args:
        player_id (int): The ID of the player to retrieve information for.

    Returns:
        dict: A dictionary containing the player information.

    Raises:
        requests.exceptions.RequestException: If there is an error making the API request.

    Examples:
        >>> player_info(8478402)
        {
            'id': 8478402,
            'fullName': 'John Doe',
            'position': 'Forward',
            'team': 'NYR',
            ...
        }
    '''
    base = f'{WEB_URL}/v1/player/{player_id}/landing'
    response = requests.get(base)
    data = response.json()
    unwanted_keys =  ['draftDetails','inTop100AllTime', 'inHHOF', 'featuredStats', 'shopLink', 'twitterLink', 'watchLink', 'last5Games', 'seasonTotals', 'awards', 'currentTeamRoster']
    for key in unwanted_keys:
        data.pop(key,None)
    for element in data:
        if isinstance(data[element],dict) and 'default' in data[element]:
            data[element] = data[element]['default']
    return data

def player_draft_details(player_id):
    '''
    Retrieve player draft details from the API.

    Args:
        player_id (int): The ID of the player to retrieve draft details for.

    Returns:
        dict: A dictionary containing the player's draft details.

    Examples:
        >>> player_draft_details(8478402)
        {
            'draftYear': 2010,
            'draftRound': 1,
            'draftOverallPick': 1,
            'draftTeam': 'EDM',
            ...
        }
    '''
    base = f'{WEB_URL}/v1/player/{player_id}/landing'
    response = requests.get(base)
    data = response.json()
    return data['draftDetails']

def player_last_five(player_id):
    """
    Retrieves the last five games played by a player.

    Args:
        player_id (int): The ID of the player.

    Returns:
        list[doct]: List of dictionaries containing data about the last 5 games a player played.

    Raises:
        None.

    Examples:
    >>> player_last_five(12345)
    [
        {'assists': 2, 'gameDate': '2024-04-06', 'gameId': 2023021226, 'gameTypeId': 2, 'goals': 0, 'homeRoadFlag': 'R', 'opponentAbbrev': 'CGY', 'pim': 0, 'plusMinus': 0, 'points': 2, 'powerPlayGoals': 0, 'shifts': 22, 'shorthandedGoals': 0, 'shots': 3, 'teamAbbrev': 'EDM', 'toi': '20:39'},
        {'assists': 0, 'gameDate': '2024-04-05', 'gameId': 2023021214, 'gameTypeId': 2, 'goals': 2, 'homeRoadFlag': 'H', 'opponentAbbrev': 'COL', 'pim': 0, 'plusMinus': 2, 'points': 2, 'powerPlayGoals': 0, 'shifts': 18, 'shorthandedGoals': 0, 'shots': 9, 'teamAbbrev': 'EDM', 'toi': '20:11'}
        ...
    ]
    """
    base = f'{WEB_URL}/v1/player/{player_id}/landing'
    response = requests.get(base)
    data = response.json()
    return data['last5Games']


def player_game_log_now(player_id):
    '''
    Access the gamelog endpoint of the NHL API. Contains currently active games and completed games for current season.

    Args:
        playerId (int): The numeric player ID

    Returns:
        list[dict]: List of dictionaries containing player specific stats by game for all games in a season.

    Examples:
    >>> player_game_log_now(8478402)
    [
        {'gameId': 2023021226, 'teamAbbrev': 'EDM', 'homeRoadFlag': 'R', 'gameDate': '2024-04-06', 'goals': 0, 'assists': 2, 'commonName': {'default': 'Oilers'}, 'opponentCommonName': {'default': 'Flames'}, 'points': 2, 'plusMinus': 0, 'powerPlayGoals': 0, 'powerPlayPoints': 2, 'gameWinningGoals': 0, 'otGoals': 0, 'shots': 3, 'shifts': 22, 'shorthandedGoals': 0, 'shorthandedPoints': 0, 'opponentAbbrev': 'CGY', 'pim': 0, 'toi': '20:39'}, 
        {'gameId': 2023021214, 'teamAbbrev': 'EDM', 'homeRoadFlag': 'H', 'gameDate': '2024-04-05', 'goals': 2, 'assists': 0, 'commonName': {'default': 'Oilers'}, 'opponentCommonName': {'default': 'Avalanche'}, 'points': 2, 'plusMinus': 2, 'powerPlayGoals': 0, 'powerPlayPoints': 0, 'gameWinningGoals': 0, 'otGoals': 0, 'shots': 9, 'shifts': 18, 'shorthandedGoals': 0, 'shorthandedPoints': 0, 'opponentAbbrev': 'COL', 'pim': 0, 'toi': '20:11'},
        ...
    ]
    '''
    base = f'{WEB_URL}/v1/player/{player_id}/game-log/now'
    response = requests.get(base)
    data = response.json()
    return data['gameLog']

if __name__ == '__main__':

    print(seasons()[-1])