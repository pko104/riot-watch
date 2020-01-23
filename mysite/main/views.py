from django.shortcuts import render
from django.http import HttpResponse



#generic

from riotwatcher import RiotWatcher, ApiError

watcher = RiotWatcher('RGAPI-4bc32ce1-4ee9-4b7c-a53d-a51b9883b43a')

my_region = 'na1'

me = watcher.summoner.by_name(my_region, 'ellls')
print(me)

# all objects are returned (by default) as a dict
# lets see if I got diamond yet (I probably didn't)
my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])
print(my_ranked_stats)




#champion id finder
def id_to_name_champ_finder(champid):
	champion_list = watcher.data_dragon.champions('10.2.1', True)
	stringified = str(champid)
	for c in champion_list["data"]:
		if champion_list["data"][c]["key"] == stringified:
			# print(c)
			return c

# id_to_name_champ_finder(101)

#return list of top 5 champs
def top_5_best_champs():
	five_array = []
	mysummid = my_ranked_stats[0]["summonerId"]
	champion_mastered = watcher.champion_mastery.by_summoner(my_region,mysummid)
	top_5_champs = champion_mastered[0:5]
	for t in top_5_champs:
		champid = t["championId"]
		five_array.append( id_to_name_champ_finder(champid) )
	return five_array





# For Riot's API, the 404 status code indicates that the requested data wasn't found and
# should be expected to occur in normal operation, as in the case of a an
# invalid summoner name, match ID, etc.
#
# The 429 status code indicates that the user has sent too many requests
# in a given amount of time ("rate limiting").

try:
    response = watcher.summoner.by_name(my_region, 'this_is_probably_not_anyones_summoner_name')
except ApiError as err:
    if err.response.status_code == 429:
        print('We should retry in {} seconds.'.format(err.response.headers['Retry-After']))
        print('this retry-after is handled by default by the RiotWatcher library')
        print('future requests wait until the retry-after time passes')
    elif err.response.status_code == 404:
        print('Summoner with that ridiculous name not found.')
    else:
        raise



# Create your views here.

def homepage(request):
	return HttpResponse(top_5_best_champs())
