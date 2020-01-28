from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .models import Tutorial
from .forms import SummonerForm
from django.views.generic import TemplateView
from riotwatcher import RiotWatcher, ApiError

watcher = RiotWatcher('RGAPI-386a7d98-cde4-4ea4-9415-4106d9c7fda0')
my_region = 'na1'
name = 'ellls'

def check_ranked_stats(name):
	me = watcher.summoner.by_name(my_region, name)
	my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])
	return my_ranked_stats


#champion id finder
def id_to_name_champ_finder(champid):
	champion_list = watcher.data_dragon.champions('10.2.1', True)
	stringified = str(champid)
	for c in champion_list["data"]:
		if champion_list["data"][c]["key"] == stringified:
			return c

# returns list of top 5 champs
def top_5_best_champs(name):
	me = watcher.summoner.by_name(my_region, name)
	my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])
	mysummid = my_ranked_stats[0]["summonerId"]
	champion_mastered = watcher.champion_mastery.by_summoner(my_region,mysummid)
	five_array = []
	champion_mastered = watcher.champion_mastery.by_summoner(my_region,mysummid)
	if champion_mastered[0:5]:
		top_5_champs = champion_mastered[0:5]
	else:
		champion_mastered[0]
	for t in top_5_champs:
		champid = t["championId"]
		print(champid)
		five_array.append( {
				"name" : id_to_name_champ_finder(champid), 
				"img" : "http://ddragon.leagueoflegends.com/cdn/img/champion/loading/"+id_to_name_champ_finder(champid)+"_0.jpg",
				"champion_level" : t["championLevel"],
				"champion_points" : t["championPoints"],
				} )
	return five_array

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

class HomeView(TemplateView):
	template_name = "home.html"

	def get(self, request):
		form = SummonerForm()
		return render(	request=request,
						template_name=self.template_name,
						context={
									"form":form
								
									})
	def post(self,request):
		form = SummonerForm(request.POST)
		if form.is_valid():
			text = form.cleaned_data['summonername']
			args = {"form":form, 
					"text": text,
					"mytopfive":top_5_best_champs(text),
					"current_summoner":check_ranked_stats(text),
					}
			return render(request,self.template_name, args)	



