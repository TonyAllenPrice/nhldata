from connector import Wrapper
from typing import List, Dict

class NHLApi:
    def __init__(self, ver: str = 'v1', lang: str = 'en', ssl_verify: bool = True):
        """
        Initializes the NHLApi object.

        Args:
            ver (str): The version of the API to use. Currently there is only 'v1'.
            lang (str): The language to use for API responses. Delfaults to 'en'.
            ssl_verify (bool): Whether to verify SSL certificates.
        """
        self._wrapper = Wrapper(ver, lang, ssl_verify)

    def _get_wrapper_data(self, type_: str, endpoint: str, ep_params: Dict = None):
        return self._wrapper.get(type=type_, endpoint=endpoint, ep_params=ep_params or {})

    def _extract_default(self, data):
        return {k: v['default'] if isinstance(v, dict) and 'default' in v else v for k, v in data.items()}

    def active_teams(self, season: int) -> List:
        """
        Returns a list of active teams for a given season.

        Args:
            season (int): The season for which to retrieve active teams.

        Returns:
            List: A list of active teams.
        """
        data = self._get_wrapper_data('stats', 'goalie/summary', {'limit': '-1', 'cayenneExp': None, 'seasonId': season})
        goalies = data['data']
        teams = {g['teamAbbrevs'] for g in goalies if len(g['teamAbbrevs']) == 3}
        return list(teams)

    def seasons(self) -> List:
        """
        Returns a list of all NHL seasons.

        Returns:
            List: A list of seasons.
        """
        return self._get_wrapper_data('web', 'season')

    def team_seasons(self, team: str) -> List:
        """
        Returns a list of all NHL seasons for a specific team.

        Args:
            team (str): Shortcode for the team, i.e. 'TOR' for the Leafs.

        Returns:
            List: A list of seasons.
        """
        return self._get_wrapper_data('web', f'roster-season/{team}')

    def teams(self) -> List[Dict]:
        """
        Returns a list of all NHL teams across all seasons.

        Returns:
            List[Dict]: A list of teams.
        """
        return self._get_wrapper_data('stats', 'team')['data']

    def roster(self, team: str, season: int = 'current') -> List[Dict]:
        """
        Returns the roster for a given team and season.

        Args:
            team (str): Shortcode for the team.
            season (int): The season for which to retrieve the roster. Defaults to 'current'.

        Returns:
            List[Dict]: A list of player information in the roster.
        """
        data = self._get_wrapper_data('web', f'roster/{team}/{season}')
        return [self._extract_default(player) for pos in data for player in data[pos]]

    def stats_players(self, season: int, pos: str, total_players: int = 1000) -> List[Dict]:
        """
        Returns the player stats for a given season, position, and total number of players.

        Args:
            season (int): The season for which to retrieve player stats.
            pos (str): The position of the players. (skater or goalie)
            total_players (int): The total number of players to retrieve. Defaults to 1000.

        Returns:
            List[Dict]: A list of player stats.
        """
        return [
            player
            for x in range(0, total_players, 100)
            for player in self._get_wrapper_data(
                'stats',
                f'{pos}/summary',
                {'limit': '100', 'start': x, 'cayenneExp': None, 'seasonId': season}
            )['data']
        ]

    def player_info(self, player_id: int) -> List[Dict]:
        """
        Returns the player information for a given player ID.

        Args:
            player_id (int): The ID of the player.

        Returns:
            List[Dict]: A dictionary containing the player information.
        """
        data = self._get_wrapper_data('web', f'player/{player_id}/landing')  # noqa: E999
        return self._extract_default(data)

    def player_draft_detail(self, player_id: int) -> List[Dict]:
        """
        Returns the draft details for a given player ID.

        Args:
            player_id (int): The ID of the player.

        Returns:
            List[Dict]: A dictionary containing the draft details.
        """
        return self._get_wrapper_data('web', f'player/{player_id}/landing')['draftDetails']

    def player_last_five(self, player_id: int) -> List[Dict]:
        """
        Returns the last five games for a given player ID.

        Args:
            player_id (int): The ID of the player.

        Returns:
            List[Dict]: A dictionary containing the last five games.
        """
        return self._get_wrapper_data('web', f'player/{player_id}/landing')['last5Games']

    def game_log_player(self, player_id: int, season: int = None, game_type: int = None) -> List[Dict]:
        """
        Returns the game log for a player in a given season and game type.

        Args:
            player_id (int): The ID of the player.
            season (int): The season for which to retrieve the game log. Defaults to current.
            game_type (int): The type of the game. (2 - Regular Season, 3 - Playoffs)

        Returns:
            List[Dict]: A dictionary containing the game log.
        """
        season_str = 'now' if season is None else str(season)
        game_type_str = '' if game_type is None else f'/{game_type}'
        return self._get_wrapper_data('web', f'player/{player_id}/game-log/{season_str}{game_type_str}')['gameLog']

    def stat_leaders(self, player_type: str, season: int = 'current', game_type: int = 2, category: str = None, limit: int = -1) -> List[Dict]:
        """
        Returns the statistical leaders for a player type in a given season and game type.

        Args:
            player_type (str): The type of player.
            season (int): The season for which to retrieve the statistical leaders. Defaults to 'current'.
            game_type (int): The type of the game. Defaults to 2 (Regular Season).
            category (str): The category of the statistics. Defaults to None.
            limit (int): The maximum number of leaders to retrieve. Defaults to All.

        Returns:
            List[Dict]: A dictionary containing the statistical leaders.
        """
        season_path = 'current' if season == 'current' else f'{season}/{game_type}'
        return self._get_wrapper_data('web', f'{player_type}-stats-leaders/{season_path}', {'categories': category, 'limit': limit})

    def player_spotlight(self) -> List[Dict]:
        """
        Returns the player spotlight information.

        Returns:
            List[Dict]: A dictionary containing the player spotlight information.
        """
        return self._get_wrapper_data('web','player-spotlight')
    
    def standings(self,date: str = 'now') -> List[Dict]:
        """
        Returns the standings for a specific date. Default is today.

        Args:
            date (str): Date of the standings in YYYY-MM-DD format. Default is today.

        Returns:
            List[Dict]: A dictionary containing the standings.
        """
        return self._get_wrapper_data('web',f'standings/{date}')
    
    def standings_info(self) -> List[Dict]:
        """
        Returns the standings information (Begining, End, Ties, Wildcard, Loser Point, etc.) for the season.

        Returns:
            List[Dict]: A dictionary containing the standings information.
        """
        return self._get_wrapper_data('web','standings-season')
    
    def stats_club(self,team:str, game_type:int = None) -> List[Dict]:
        """
        Returns the statistics for a club/team.

        Args:
            team (str): The name of the team.
            season (int): The season for which to retrieve the statistics. Defaults to 'now'.
            game_type (int): The type of the game. Defaults to None for current standings.

        Returns:
            List[Dict]: A dictionary containing the statistics.
        """
        endpoint = f'club-stats/{team}/now' if game_type is None else f'club-stats/{team}/{game_type}'
        return self._get_wrapper_data('web',endpoint)
    
    def club_gametypes(self, team:str) -> List[Dict]:
        """
        Returns the game types for a club/team by season.

        Args:
            team (str): The shortname of the team.

        Returns:
            List[Dict]: A dictionary containing the game types.
        """
        return self._get_wrapper_data('web',f'club-stats-season/{team}')

    def club_scoreboard(self, team:str) -> List[Dict]:
        """
        Returns the scoreboard for a given club/team.

        Args:
            team (str): The shortname of the team.

        Returns:
            List[Dict]: A dictionary containing the scoreboard.
        """
        return self._get_wrapper_data('web',f'scoreboard/{team}/now')
    
    def club_prospects(self, team: str) -> List[Dict]:
        """
        Returns the prospects for a given club/team.

        Args:
            team (str): The shortname of the team.

        Returns:
            List[Dict]: A list of player prospects.
        """
        data = self._get_wrapper_data('web', f'prospects/{team}')
        return [self._extract_default(player) for pos in data for player in data[pos]]

    def club_schedule(self, team:str, length:str = 'season', window:str = 'now') -> List[Dict]:
        """
        Returns the schedule for a club/team.

        Args:
            team (str): The name of the team.
            length (str): The length of the schedule. Defaults to 'season'. Also accepts Month or Week.
            window (str): The window of the schedule. Defaults to 'now'. Also accepts YYYY-MM or YYYY-MM-DD.

        Returns:
            List[Dict]: A dictionary containing the schedule.
        """
        ep = f'club-schedule-season/{team}/{window}' if length == 'season' else f'club-schedule/{team}/{length}/{window}'
        return self._get_wrapper_data('web',ep)        

    def league_schedule(self, sched_type:str = 'schedule', date:str = 'now') -> List[Dict]:
        """
        Returns the schedule for the league.

        Args:
            sched_type (str): The type of the schedule (schedule or calendar). Defaults to 'schedule'.
            date (str): The date for which to retrieve the schedule. Defaults to 'now'. Format: YYYY-MM-DD

        Returns:
            List[Dict]: A dictionary containing the schedule.
        """
        sched_type = 'schedule-calendar' if sched_type == 'calendar' else 'schedule'
        return self._get_wrapper_data('web', f'{sched_type}/{date}')
    
    def scores(self,date:str = 'now') -> List[Dict]:
        """
        Returns the scores information for a given date.

        Args:
            date (str): The date for which to retrieve the scores. Defaults to 'now'. Format: YYYY-MM-DD

        Returns:
            List[Dict]: A dictionary containing the scores information.
        """
        return self._get_wrapper_data('web',f'score/{date}')
    
    def scoreboard(self) -> List[Dict]:
        """
        Returns current league scoreboard information.

        Returns:
            List[Dict]: A dictionary containing the scoreboard information.
        """
        return self._get_wrapper_data('web','scoreboard/now')
    
    def tv_schedule(self, date:str = 'now') -> List[Dict]:
        """
        Returns the TV schedule information.

        Args:
            date (str): The date for which to retrieve the TV schedule. Defaults to 'now'. Format: YYYY-MM-DD

        Returns:
            List[Dict]: A dictionary containing the TV schedule information.
        """
        return self._get_wrapper_data('web',f'network/tv-schedule/{date}')
    
    def streamers(self) -> List[Dict]:
        """
        Returns the streamer information by country/region.

        Returns:
            List[Dict]: A dictionary containing the streamers information.
        """
        return self._get_wrapper_data('web','where-to-watch')
    
    def gamecenter(self, game_id:int, section:str = 'play-by-play') -> List[Dict]:
        """
        Returns the gamecenter information for a given game ID and section.

        Args:
            game_id (int): The ID of the game.
            section (str): The section of the gamecenter. Defaults to 'play-by-play'.
                Options: 'play-by-play','boxscore','landing'

        Returns:
            List[Dict]: A dictionary containing the gamecenter information.
        """
        return self._get_wrapper_data('web',f'gamecenter/{game_id}/{section}')
    
    def odds(self,country = 'US') -> List[Dict]:
        """
        Returns the odds information for a given country.

        Args:
            country (str): The country for which to retrieve the odds. Defaults to 'US'.

        Returns:
            List[Dict]: A dictionary containing the odds information.
        """
        return self._get_wrapper_data('web',f'partner-game/{country}/now')
    
    def draft_rankings(self, year:str = 'now', category:str = None) -> List[Dict]:
        """
        Returns the draft rankings for a given year and category.

        Args:
            year (str): The year for which to retrieve the draft rankings. Defaults to 'now'. Format: YYYY
            category (str): The category of the draft rankings. Defaults to None.
                Options: 1 - NA Skater, 2 - Intl Skater, 3 - NA Goalie, 4 - Intl Goalie

        Returns:
            List[Dict]: A dictionary containing the draft rankings.
        """
        year = 'now' if year == 'now' else f'{year}/{category}'
        return self._get_wrapper_data('web',f'draft/rankings/{year}')
    
    def metadata(self,players:str = None, teams:str = None, game_id:int = None) -> List[Dict]:
        """
        Returns the metadata for players, teams, or a specific game.

        Args:
            players (str): The players for which to retrieve the metadata. Defaults to None.
            teams (str): The teams for which to retrieve the metadata. Defaults to None.
            game_id (int): The ID of the game for which to retrieve the metadata. Defaults to None.

        Returns:
            List[Dict]: A dictionary containing the metadata.
        """
        if game_id is not None:
            return self._get_wrapper_data('web',f'meta/game/{game_id}')
        ep_params = {
            'players':players,
            'teams':teams
        }
        return self._get_wrapper_data('web','meta',ep_params)
