import nhlstats

mp = nhlstats.moneypuck.Connector()
nhl_web = nhlstats.nhl.WebConnector()
nhl_stats = nhlstats.nhl.StatsConnector()

print(nhl_web.seasons())