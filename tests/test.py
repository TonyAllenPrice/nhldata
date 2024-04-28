import nhldata

mp = nhldata.moneypuck.Connector()
nhl_web = nhldata.nhl.WebConnector()
nhl_stats = nhldata.nhl.StatsConnector()

print(mp.season_stats(file_type='skaters',seasons=[2022,2023],gametype='regular'))