import nhldata

mp = nhldata.moneypuck.Connector()
nhl_web = nhldata.nhl.WebConnector()
nhl_stats = nhldata.nhl.StatsConnector()

print(nhl_web.seasons())