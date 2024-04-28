from .wrapper import Wrapper
from ..tools.exceptions import NHLStatsException
from typing import List, Dict

class Connector(object):
    def __init__(self, type_: str, ver: str = 'v1', lang: str = 'en', ssl_verify: bool = True):
        """
        Initializes the NHLApi object.

        Args:
            ver (str): The version of the API to use. Currently there is only 'v1'.
            lang (str): The language to use for API responses. Delfaults to 'en'.
            ssl_verify (bool): Whether to verify SSL certificates.
        """
        self._type = type_
        self._wrapper = Wrapper(ver, lang, ssl_verify)

    def _get_wrapper_data(self, endpoint: str, ep_params: Dict = None):
        """
        Get wrapper data from the NHL API.

        Args:
            endpoint (str): The endpoint to retrieve data from.
            type_ (str, optional): The type of data to retrieve.
            ep_params (Dict, optional): Additional parameters for the endpoint.

        Returns:
            The data retrieved from the NHL API.

        Raises:
            None.

        Examples:
            >>> _get_wrapper_data('players')
            {'data': [{'id': 1, 'name': 'John Doe'}, {'id': 2, 'name': 'Jane Smith'}]}
        """
        return self._wrapper.get(type=self._type, endpoint=endpoint, ep_params=ep_params or {})

    def _check_gametype(self,gametype:str):
        gametypes = {'regular': 2, 'playoffs': 3}
        return gametypes.get(gametype, NHLStatsException)
        

class WebConnector(Connector):

    def __init__(self, ver: str = 'v1', lang: str = 'en', ssl_verify: bool = True):
        super().__init__('web', ver, lang, ssl_verify)

    def _extract_default(self, data):
        """
        Extract default values from a dictionary.

        Args:
            data (dict): The dictionary to extract default values from.

        Returns:
            dict: A new dictionary with the default values extracted.

        Raises:
            None.
        """
        return {k: v['default'] if isinstance(v, dict) and 'default' in v else v for k, v in data.items()}

    def seasons(self) -> List:
        """
        Returns a list of all NHL seasons.

        Returns:
            List: A list of seasons.
        """
        return self._get_wrapper_data('season')

    def team_seasons(self, team: str) -> List:
        """
        Returns a list of all NHL seasons for a specific team.

        Args:
            team (str): Shortcode for the team, i.e. 'TOR' for the Leafs.

        Returns:
            List: A list of seasons.
        """
        return self._get_wrapper_data(f'roster-season/{team}')

    def roster(self, team: str, season: int = None) -> List[Dict]:
        """
        Returns the roster for a given team and season.

        Args:
            team (str): Shortcode for the team.
            season (int): The season for which to retrieve the roster.

        Returns:
            List[Dict]: A list of player information in the roster.
        """
        season_str = 'current' if season is None else season
        data = self._get_wrapper_data(f'roster/{team}/{season_str}')
        return [self._extract_default(player) for pos in data for player in data[pos]]


    def player_info(self, player_id: int) -> List[Dict]:
        """
        Returns the player information for a given player ID.

        Args:
            player_id (int): The ID of the player.

        Returns:
            List[Dict]: A dictionary containing the player information.
        """
        data = self._get_wrapper_data(f'player/{player_id}/landing')  # noqa: E999
        return self._extract_default(data)

    def player_draft_detail(self, player_id: int) -> List[Dict]:
        """
        Returns the draft details for a given player ID.

        Args:
            player_id (int): The ID of the player.

        Returns:
            List[Dict]: A dictionary containing the draft details.
        """
        return self._get_wrapper_data(f'player/{player_id}/landing')['draftDetails']

    def player_last_five(self, player_id: int) -> List[Dict]:
        """
        Returns the last five games for a given player ID.

        Args:
            player_id (int): The ID of the player.

        Returns:
            List[Dict]: A dictionary containing the last five games.
        """
        return self._get_wrapper_data(f'player/{player_id}/landing')['last5Games']

    def game_log_player(self, player_id: int, season: int = None, game_type: str = None) -> List[Dict]:
        """
        Returns the game log for a player in a given season and game type.

        Args:
            player_id (int): The ID of the player.
            season (int): The season for which to retrieve the game log.
            game_type (int): The type of the game - Regular or PLayoffs

        Returns:
            List[Dict]: A dictionary containing the game log.
        """
        season_str = 'now' if season is None else str(season)
        game_type_str = '' if game_type is None else f'/{self._check_gametype(game_type)}'
        return self._get_wrapper_data(f'player/{player_id}/game-log/{season_str}{game_type_str}')['gameLog']

    def stat_leaders(self, player_type: str, season: int = None, game_type: str = 'regular', category: str = None, limit: int = -1) -> List[Dict]:
        """
        Returns the statistical leaders for a player type in a given season and game type.

        Args:
            player_type (str): The type of player.
            season (int): The season for which to retrieve the statistical leaders.
            game_type (int): The type of the game. 
            category (str): The category of the statistics. 
            limit (int): The maximum number of leaders to retrieve.

        Returns:
            List[Dict]: A dictionary containing the statistical leaders.
        """
        season_path = 'current' if season is None else f'{season}/{self._check_gametype(game_type)}'
        return self._get_wrapper_data(f'{player_type}-stats-leaders/{season_path}', {'categories': category, 'limit': limit})

    def player_spotlight(self) -> List[Dict]:
        """
        Returns the player spotlight information.

        Returns:
            List[Dict]: A dictionary containing the player spotlight information.
        """
        return self._get_wrapper_data('player-spotlight')
    
    def standings(self,date: str = 'now') -> List[Dict]:
        """
        Returns the standings for a specific date.

        Args:
            date (str): Date of the standings in YYYY-MM-DD format.

        Returns:
            List[Dict]: A dictionary containing the standings.
        """
        return self._get_wrapper_data(f'standings/{date}')
    
    def standings_info(self) -> List[Dict]:
        """
        Returns the standings information (Begining, End, Ties, Wildcard, Loser Point, etc.) for the season.

        Returns:
            List[Dict]: A dictionary containing the standings information.
        """
        return self._get_wrapper_data('standings-season')
    
    def stats_club(self,team:str, game_type:str = None) -> List[Dict]:
        """
        Returns the statistics for a club/team.

        Args:
            team (str): The name of the team.
            season (int): The season for which to retrieve the statistics.
            game_type (str): The type of the game.

        Returns:
            List[Dict]: A dictionary containing the statistics.
        """
        endpoint = f'club-stats/{team}/now' if game_type is None else f'club-stats/{team}/{self._check_gametype(game_type)}'
        return self._get_wrapper_data(endpoint)
    
    def club_gametypes(self, team:str) -> List[Dict]:
        """
        Returns the game types for a club/team by season.

        Args:
            team (str): The shortname of the team.

        Returns:
            List[Dict]: A dictionary containing the game types.
        """
        return self._get_wrapper_data(f'club-stats-season/{team}')

    def club_scoreboard(self, team:str) -> List[Dict]:
        """
        Returns the scoreboard for a given club/team.

        Args:
            team (str): The shortname of the team.

        Returns:
            List[Dict]: A dictionary containing the scoreboard.
        """
        return self._get_wrapper_data(f'scoreboard/{team}/now')
    
    def club_prospects(self, team: str) -> List[Dict]:
        """
        Returns the prospects for a given club/team.

        Args:
            team (str): The shortname of the team.

        Returns:
            List[Dict]: A list of player prospects.
        """
        data = self._get_wrapper_data(f'prospects/{team}')
        return [self._extract_default(player) for pos in data for player in data[pos]]

    def club_schedule(self, team:str, length:str = None, window:str = None) -> List[Dict]:
        """
        Returns the schedule for a club/team.

        Args:
            team (str): The name of the team.
            length (str): The length of the schedule. Also accepts Month or Week.
            window (str): The window of the schedule. Also accepts YYYY-MM or YYYY-MM-DD.

        Returns:
            List[Dict]: A dictionary containing the schedule.
        """
        window_str = 'now' if window is None else window
        length = 'season' if length is None else length
        ep = f'club-schedule-season/{team}/{window_str}' if length == 'season' else f'club-schedule/{team}/{length}/{window_str}'
        return self._get_wrapper_data(ep)

    def league_schedule(self, sched_type:str = 'schedule', date:str = 'now') -> List[Dict]:
        """
        Returns the schedule for the league.

        Args:
            sched_type (str): The type of the schedule (schedule or calendar).
            date (str): The date for which to retrieve the schedule. Format: YYYY-MM-DD

        Returns:
            List[Dict]: A dictionary containing the schedule.
        """
        sched_type = 'schedule-calendar' if sched_type == 'calendar' else 'schedule'
        return self._get_wrapper_data(f'{sched_type}/{date}')
    
    def scores(self,date:str = 'now') -> List[Dict]:
        """
        Returns the scores information for a given date.

        Args:
            date (str): The date for which to retrieve the scores. Format: YYYY-MM-DD

        Returns:
            List[Dict]: A dictionary containing the scores information.
        """
        return self._get_wrapper_data(f'score/{date}')
    
    def scoreboard(self) -> List[Dict]:
        """
        Returns current league scoreboard information.

        Returns:
            List[Dict]: A dictionary containing the scoreboard information.
        """
        return self._get_wrapper_data('scoreboard/now')
    
    def tv_schedule(self, date:str = 'now') -> List[Dict]:
        """
        Returns the TV schedule information.

        Args:
            date (str): The date for which to retrieve the TV schedule. Format: YYYY-MM-DD

        Returns:
            List[Dict]: A dictionary containing the TV schedule information.
        """
        return self._get_wrapper_data(f'network/tv-schedule/{date}')
    
    def streamers(self) -> List[Dict]:
        """
        Returns the streamer information by country/region.

        Returns:
            List[Dict]: A dictionary containing the streamers information.
        """
        return self._get_wrapper_data('where-to-watch')
    
    def gamecenter(self, game_id:int, section:str = 'play-by-play') -> List[Dict]:
        """
        Returns the gamecenter information for a given game ID and section.

        Args:
            game_id (int): The ID of the game.
            section (str): The section of the gamecenter.
                Options: 'play-by-play','boxscore','landing'

        Returns:
            List[Dict]: A dictionary containing the gamecenter information.
        """
        return self._get_wrapper_data(f'gamecenter/{game_id}/{section}')
    
    def odds(self,country = 'US') -> List[Dict]:
        """
        Returns the odds information for a given country.

        Args:
            country (str): The country for which to retrieve the odds.

        Returns:
            List[Dict]: A dictionary containing the odds information.
        """
        return self._get_wrapper_data(f'partner-game/{country}/now')
    
    def draft_rankings(self, year:str = 'now', category:str = None) -> List[Dict]:
        """
        Returns the draft rankings for a given year and category.

        Args:
            year (str): The year for which to retrieve the draft rankings. Format: YYYY
            category (str): The category of the draft rankings.
                Options: 1 - NA Skater, 2 - Intl Skater, 3 - NA Goalie, 4 - Intl Goalie

        Returns:
            List[Dict]: A dictionary containing the draft rankings.
        """
        year = 'now' if year == 'now' else f'{year}/{category}'
        return self._get_wrapper_data(f'draft/rankings/{year}')
    
    def metadata(self,players:str = None, teams:str = None, game_id:int = None) -> List[Dict]:
        """
        Returns the metadata for players, teams, or a specific game.

        Args:
            players (str): The players for which to retrieve the metadata.
            teams (str): The teams for which to retrieve the metadata.
            game_id (int): The ID of the game for which to retrieve the metadata. 

        Returns:
            List[Dict]: A dictionary containing the metadata.
        """
        if game_id is not None:
            return self._get_wrapper_data(f'meta/game/{game_id}')
        ep_params = {
            'players':players,
            'teams':teams
        }
        return self._get_wrapper_data('meta',ep_params)

class StatsConnector(Connector):

    def __init__(self, ver: str = 'v1', lang: str = 'en', ssl_verify: bool = True):
        super().__init__('stats', ver, lang, ssl_verify)
    
    def teams(self) -> List[Dict]:
        """
        Returns a list of all NHL teams across all seasons.

        Returns:
            List[Dict]: A list of teams.
        """
        return self._get_wrapper_data('team')['data']
    
    def active_teams(self, season: int) -> List:
        """
        Returns a list of active teams for a given season.

        Args:
            season (int): The season for which to retrieve active teams.

        Returns:
            List: A list of active teams.
        """
        ep_params = {
            'limit': '-1',
            'cayenneExp': f'seasonId={season}'
            }
        data = self._get_wrapper_data('goalie/summary', ep_params=ep_params)
        goalies = data['data']
        teams = {g['teamAbbrevs'] for g in goalies if len(g['teamAbbrevs']) == 3}
        return list(teams)

    def stats_players(self, season: int, pos: str, total_players: int = 1000, isAggregate: bool = None, isGame: bool = None, factCayenneExp: str = None, include: str = None, exclude: str = None, sort: str = None, dir_: str = None) -> List[Dict]:
        """
        Retrieves player statistics based on the specified parameters.

        Args:
            season (int): The season ID for which to retrieve player statistics.
            pos (str): The position of the players to retrieve statistics for.
            total_players (int, optional): The total number of players to retrieve.
            isAggregate (bool, optional): Whether to retrieve aggregate statistics. 
            isGame (bool, optional): Whether to retrieve game statistics. 
            factCayenneExp (str, optional): The Cayenne expression for additional filtering. 
            include (str, optional): The fields to include in the response. 
            exclude (str, optional): The fields to exclude from the response. 
            sort (str, optional): The field to sort the response by. 
            dir_ (str, optional): The direction to sort the response in. 

        Returns:
            List[Dict]: A list of dictionaries containing player statistics.
        """
        players = []
        for x in range(0, total_players, 100):
            ep_params = {
                'limit': '100', 
                'start': x, 
                'cayenneExp': None, 
                'seasonId': season,
                'isAggregate': isAggregate,
                'isGame': isGame,
                'include': include,
                'exclude': exclude,
                'sort': sort,
                'dir': dir_
            }
            players.extend(
                self._get_wrapper_data(
                    f'{pos}/summary',
                    ep_params=ep_params
                )['data']
            )
        return players

    def players(self) -> List[Dict]:
        """
        Retrieves information about all players.

        Returns:
            List[Dict]: A list of dictionaries containing player information.
        """
        return self._get_wrapper_data('players')
    
    def leaders(self, pos: str, attr: str) -> List[Dict]:
        """
        Retrieves the leaders in a specific statistical category for a given position.

        Args:
            pos (str): The position of the players to retrieve leaders for.
            attr (str): The statistical attribute to retrieve leaders for.

        Returns:
            List[Dict]: A list of dictionaries containing information about the leaders.
        """
        return self._get_wrapper_data(f'leaders/{pos}/{attr}')['data']

    def milestones(self, pos: str) -> List[Dict]:
        """
        Retrieves milestone information for players of a specific position.

        Args:
            pos (str): The position of the players to retrieve milestone information for.

        Returns:
            List[Dict]: A list of dictionaries containing milestone information.
        """
        return self._get_wrapper_data(f'milestones/{pos}')
    
    def draft(self) -> List[Dict]:
        """
        Retrieves years and rounds for the NHL draft.

        Returns:
            List[Dict]: A list of dictionaries containing draft information.
        """
        return self._get_wrapper_data('draft')
    
    def stats_team(self, season: int, total_teams: int = -1, isAggregate: bool = None, isGame: bool = None, factCayenneExp: str = None, include: str = None, exclude: str = None, sort: str = None, dir_: str = None, start: int = None) -> List[Dict]:
        """
        Retrieves team statistics based on the specified parameters.

        Args:
            season (int): The season ID for which to retrieve team statistics.
            total_teams (int, optional): The total number of teams to retrieve. 
            isAggregate (bool, optional): Whether to retrieve aggregate statistics. 
            isGame (bool, optional): Whether to retrieve game statistics. 
            factCayenneExp (str, optional): The Cayenne expression for additional filtering. 
            include (str, optional): The fields to include in the response. 
            exclude (str, optional): The fields to exclude from the response. 
            sort (str, optional): The field to sort the response by. 
            dir_ (str, optional): The direction to sort the response in. 
            start (int, optional): The starting index for retrieving teams. 

        Returns:
            List[Dict]: A list of dictionaries containing team statistics.
        """
        ep_params = {
            'limit': total_teams, 
            'cayenneExp': None, 
            'seasonId': season,
            'isAggregate': isAggregate,
            'isGame': isGame,
            'include': include,
            'exclude': exclude,
            'sort': sort,
            'dir': dir_,
            'start': start
            }
        return self._get_wrapper_data('team/summary',ep_params=ep_params)['data']

    def franchise(self) -> List:
        """
        Retrieves information about NHL franchises.

        Returns:
            List: A list containing franchise information.
        """       
        return self._get_wrapper_data('franchise')
    
    def component_season(self) -> List[Dict]:
        """
        Retrieves information about NHL component seasons.

        Returns:
            List[Dict]: A list of dictionaries containing component season information.
        """
        return self._get_wrapper_data('componentSeason')
    
    def season(self) -> List[Dict]:
        """
        Retrieves information about NHL seasons.

        Returns:
            List[Dict]: A list of dictionaries containing season information.
        """
        return self._get_wrapper_data('season')['data']

    def game(self, meta: bool = False) -> List[Dict]:
        """
        Retrieves information about NHL games.

        Args:
            meta (bool, optional): Whether to retrieve metadata about the games.

        Returns:
            List[Dict]: A list of dictionaries containing game information.
        """
        if meta:
            return self._get_wrapper_data('game/meta')
        else:
            return self._get_wrapper_data('game')

    def config(self) -> List[Dict]:
        """
        Retrieves configuration information for the NHL Stats API.

        Returns:
            List[Dict]: A list of dictionaries containing configuration information.

        """
        return self._get_wrapper_data('config')
    
    def shift_charts(self, game_id: int) -> List[Dict]:
        """
        Retrieves shift charts for a specific game.

        Args:
            game_id (int): The ID of the game to retrieve shift charts for.

        Returns:
            List[Dict]: A list of dictionaries containing shift chart information.

        """
        ep_params = {
            'gameId':game_id,
            'cayenneExp':None
        }
        return self._get_wrapper_data('shiftcharts',ep_params=ep_params)
    
    def glossary(self) -> List[Dict]:
        """
        Retrieves the NHL Stats glossary.

        Returns:
            List[Dict]: A list of dictionaries containing glossary terms and definitions.

        """
        return self._get_wrapper_data('glossary')