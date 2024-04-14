from nhl_api import NHLApi

api = NHLApi()
curr_season = api.current_season()
print(api.game_long_player(8478402,20232024,2))