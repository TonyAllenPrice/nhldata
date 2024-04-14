from connector import Wrapper
from typing import List, Dict

class NHLApi:
    def __init__(self,ver: str = 'v1', lang: str = 'en', ssl_verify: bool = True):
        self._wrapper = Wrapper(ver, lang, ssl_verify)

    def active_teams(self, season:str) -> List:
        endpoint = 'goalie/summary'
        ep_params = {
            'limit': '-1',
            'cayenneExp': '',
            'seasonId': season
        }
        data = self._wrapper.get(type='stats', endpoint=endpoint, ep_params=ep_params)
        goalies = data['data']
        teams = {g['teamAbbrevs'] for g in goalies if len(g['teamAbbrevs']) == 3}
        return list(teams)

    def seasons(self) -> List:
        return self._wrapper.get(type='web',endpoint='season')
    
    def current_season(self) -> str:
        return self.seasons()[-1]

    def team_seasons(self, team: str) -> List:
        return self._wrapper.get(type='web',endpoint=f'roster-season/{team}')
    
    def teams(self) -> List[Dict]:
        return self._wrapper.get(type='stats', endpoint='team')['data']
    
    def current_roster(self,team:str) -> Dict:
        return self._wrapper.get(type='web',endpoint=f'roster/{team}/current')

    def roster(self,team: str, season: str) -> List[Dict]:
        data = self._wrapper.get(type='web', endpoint=f'roster/{team}/{season}')
        changes = ['firstName', 'lastName', 'birthCity', 'birthStateProvince']
        players = [player for pos in data for player in data[pos]]
        for player in players:
            for change in changes:
                if change in player:
                    player[change] = player[change]['default']
        return players
      
    def stats_players(self,season:str,pos:str,total_players:int=1000) -> List[Dict]:
        return [
            player
            for x in range(0, total_players, 100)
            for player in self._wrapper.get(
                type='stats',
                endpoint=f'{pos}/summary',
                ep_params={
                    'limit': '100',
                    'start': x,
                    'cayenneExp': '',
                    'seasonId': season
                }
            )['data']
        ]
    
    def game_long_player(self,player_id:str,season:str,game_type:int) -> List[Dict]:
        return self._wrapper.get(type='web',endpoint=f'player/{player_id}/game-log/{season}/{game_type}')['gameLog']
