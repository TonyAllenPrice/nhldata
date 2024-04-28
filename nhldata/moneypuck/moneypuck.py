import csv
import requests
import io
import zipfile
import datetime
from ..tools.exceptions import NHLStatsException

class Connector:
    def __init__(self):
        self.base_url = 'https://moneypuck.com/moneypuck/playerData/'
        self.max_year = int(datetime.date.today().year)

    def _validate(self,gametype=None, season=None, position=None, file_type=None, single_year=True):
        '''
        Validates the input parameters for gametype, season, position, and file_type.

        Args:
        - `gametype`: The type of game. Valid options are 'regular' and 'playoffs'.
        - `season`: The season or list of seasons to validate.
        - `position`: The position of the player. Valid options are 'skaters' and 'goalies'.
        - `file_type`: The type of file. Valid options are 'skaters', 'goalies', 'lines', and 'teams'.
        - `single_year`: A boolean indicating whether the season is a single year or a list of years.

        Raises:
        - `ValueError`: If any of the input parameters are invalid.
        '''
        valid_gametypes = {'regular', 'playoffs'}
        valid_positions = {'skaters', 'goalies'}
        valid_file_types = {'skaters', 'goalies', 'lines', 'teams'}
        valid_range = range(2006, self.max_year) if single_year else range(2007, self.max_year)
        
        if gametype and gametype not in valid_gametypes:
            raise NHLStatsException(f"Invalid gametype. Valid options are: {valid_gametypes}.")
        if season and (single_year and season not in valid_range or not single_year and set(season).difference(valid_range)):
            raise NHLStatsException(f"Invalid season. Valid seasons are {valid_range}.")
        if position and position not in valid_positions:
            raise NHLStatsException(f"Invalid position. Valid options are: {valid_positions}.")
        if file_type and file_type not in valid_file_types:
            raise NHLStatsException(f"Invalid file type. Valid options are: {valid_file_types}.")

    def _fetch_and_process_data(self,endpoint:str, file_name:str):
        '''
        Fetches and processes data from a specified endpoint.

        Args:
        - `endpoint`: The endpoint to fetch data from.
        - `file_name`: The name of the file to fetch.

        Returns:
        - A list of dictionaries representing the fetched data.
        '''
        url = f'{self.base_url}{endpoint}{file_name}.csv'
        r = requests.get(url)
        data_stream = io.StringIO(r.text)
        return [dict(row.items()) for row in csv.DictReader(data_stream, skipinitialspace=True)]

    def season_stats(self,file_type:str, seasons:list, gametype:str):
        '''
        Fetches and processes season statistics data.

        Args:
        - `file_type`: The type of file to fetch.
        - `seasons`: A list of seasons to fetch data for.
        - `gametype`: The type of game to fetch data for.

        Returns:
        - A list of dictionaries representing the fetched data.
        '''
        self._validate(file_type=file_type, gametype=gametype, season=seasons, single_year=False)
        return [data for season in seasons for data in self._fetch_and_process_data(f'seasonSummary/{season}/{gametype}/', file_type)]

    def player_by_game(self,player_id:int, position:str, gametype:str):
        '''
        Fetches and processes player data by game.

        Args:
        - `player_id`: The ID of the player to fetch data for.
        - `position`: The position of the player.
        - `gametype`: The type of game to fetch data for.

        Returns:
        - A list of dictionaries representing the fetched data.
        '''
        self._validate(gametype=gametype, position=position)
        return self._fetch_and_process_data(f'careers/gameByGame/{gametype}/{position}/', player_id)

    def player_by_season(self,player_id:int, position:str, gametype:str):
        '''
        Fetches and processes player data by season.

        Args:
        - `player_id`: The ID of the player to fetch data for.
        - `position`: The position of the player.
        - `gametype`: The type of game to fetch data for.

        Returns:
        - A list of dictionaries representing the fetched data.
        '''
        self._validate(gametype=gametype, position=position)
        return self._fetch_and_process_data(f'careers/perSeason/{gametype}/{position}/', player_id)

    def team_stats(self,team:str, gametype:str):
        '''
        Fetches and processes team statistics data.

        Args:
        - `team`: The team to fetch data for.
        - `gametype`: The type of game to fetch data for.

        Returns:
        - A list of dictionaries representing the fetched data.
        '''
        self._validate(gametype=gametype)
        return self._fetch_and_process_data(f'careers/gameByGame/{gametype}/teams/', team)

    def shots_season(self,season:int):
        '''
        Fetches and processes shot data for a specific season.

        Args:
        - `season`: The season to fetch shot data for.

        Returns:
        - A list of dictionaries representing the fetched data.
        '''
        self._validate(season=season)
        r = requests.get(f'https://peter-tanner.com/moneypuck/downloads/shots_{season}.zip')
        with zipfile.ZipFile(io.BytesIO(r.content)) as zipped, zipped.open(f'shots_{season}.csv') as infile:
            data_stream = io.TextIOWrapper(infile, 'utf-8')
            return [dict(row.items()) for row in csv.DictReader(data_stream, skipinitialspace=True)]