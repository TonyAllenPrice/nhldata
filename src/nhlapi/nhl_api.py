from connector import Wrapper
from typing import List, Dict
import itertools

class NHLApi:
    def __init__(self,ver: str = 'v1', lang: str = 'en', ssl_verify: bool = True):
        self._wrapper = Wrapper(ver, lang, ssl_verify)

    def active_teams(self, season:str) -> List:
        endpoint = 'goalie/summary'
        ep_params = {
                'limit':'-1',
                'cayenneExp':'',
                'seasonId':season
            }
        data = self._wrapper.get(type='stats', endpoint = endpoint, ep_params = ep_params)
        goalies = data['data']
        teams = [g['teamAbbrevs'] for g in goalies]
        teams = list(set(teams))
        return [t for t in teams if len(t) == 3]

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
        players = [data[pos] for pos in data]
        changes = ['firstName','lastName','birthCity','birthStateProvince'] # These 4 have nested natures with FR translations. We are pulling just English/Default.
        players = list(itertools.chain.from_iterable(players))
        for player, change in itertools.product(players, changes):
            if change in player: # Not every player has a State/Province, but this allows one loop to do all 4 changes.
                player[change] = player[change]['default']
        return players
      
    def stats_players(self,season:str,pos:str,total_players:int=1000) -> List[Dict]:
        results = []
        for x in range(0,total_players,100):
            ep_params = {
                'limit':'100',
                'start':x,
                'cayenneExp':'',
                'seasonId':season
            }
            data = self._wrapper.get(type='stats',endpoint=f'{pos}/summary', ep_params=ep_params)
            results.append(data['data'])
        
        return list(itertools.chain.from_iterable(results))
    
    def game_long_player(self,player_id:str,season:str,game_type:int) -> List[Dict]:
        return self._wrapper.get(type='web',endpoint=f'player/{player_id}/game-log/{season}/{game_type}')['gameLog']
