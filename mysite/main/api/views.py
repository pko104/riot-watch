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

# Lets get some champions
static_champ_list = watcher.static_data.champions(my_region)
print(static_champ_list)

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



# from rest_framework import generics


# from main.models import Tutorials
# from .serializers import TutorialSerializer

# class TutorialPostRudView(generics.RetrieveUpdateDestroyAPIView): #detailview
# 	lookup_field		='pk' #slug, id # url
# 	serializer_class	= TutorialSerializer

# 	def get_queryset(self):
# 		return Tutorials.objects.all()

# 	# def get_object(self):
# 	# 	pk = self.kwargs.get("pk")