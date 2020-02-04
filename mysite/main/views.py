from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .models import Tutorial
from .forms import SummonerForm
from django.views.generic import TemplateView
from riotwatcher import RiotWatcher, ApiError

watcher = RiotWatcher('RGAPI-5354f50f-3bb9-4fb8-98e6-c3bac5c08ba0')
my_region = 'na1'
name = 'ellls'


sum_spell_json = {	4 : "http://ddragon.leagueoflegends.com/cdn/10.2.1/img/spell/SummonerFlash.png",
					21 : "http://ddragon.leagueoflegends.com/cdn/10.2.1/img/spell/SummonerBarrier.png",
					7 : "http://ddragon.leagueoflegends.com/cdn/10.2.1/img/spell/SummonerHeal.png"}

def summonerSpellKey(dict, key):      
    if key in dict.keys(): 
        return dict[key]
    else:
        return key

#check ranked stats
def check_ranked_stats(name):
	me = watcher.summoner.by_name(my_region, name)
	my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])
	total_games = my_ranked_stats[0]['wins'] + my_ranked_stats[0]['losses']
	win_ratio = float(my_ranked_stats[0]['wins']/total_games)*100
	win_ratio = round(win_ratio,2)
	my_ranked_stats[0].update({	"total_games":total_games,
								"win_ratio":win_ratio})
	return my_ranked_stats

#champion id finder
def id_to_name_champ_finder(champid):
	champion_list = watcher.data_dragon.champions('10.2.1', True)
	stringified = str(champid)
	for c in champion_list["data"]:
		if champion_list["data"][c]["key"] == stringified:
			return c	

def get_match_list_by_acc(name):
	me = watcher.summoner.by_name(my_region, name)
	my_match_stats = watcher.match.matchlist_by_account(my_region, me['accountId'])
	five_array = []
	five_array = my_match_stats["matches"][0:10]
	return five_array

#get match desc
def get_match_descriptions(name):
	match_array=[]
	five_array = get_match_list_by_acc(name)
	for f in five_array:
		match_array.append( watcher.match.by_id(my_region, f['gameId']) )
	return match_array

#pull out specific match data from JSON
def pull_out_match_data(name):
	match_dict = []
	match_desc = get_match_descriptions(name)
	summId = check_ranked_stats(name)[0]['summonerId']

	for m in match_desc:
		#grab team both team data
		match_data = []
		team1_data = m['teams'][0]
		team2_data = m['teams'][1]
		#reset array to push into dict per participant
		#identities have their own loop
		for p in m['participantIdentities']:
			if p['player']['summonerId'] == summId:			
				#check to see which participant the name value is
				participant_id = p['participantId'] 

		#participants have their own loop
		for k in m['participants']:

			#check which team is which
			if k['teamId'] == team1_data['teamId']:
				participant_team = team1_data
			else:
				participant_team = team2_data		

			#only grab data from the participant
			if participant_id == k['participantId']:
				match_data = {		'participantId': k['participantId'],
									'championId': k['championId'],
									'champImg': "http://ddragon.leagueoflegends.com/cdn/10.2.1/img/champion/"+id_to_name_champ_finder(k['championId'])+".png",
									'teamId': k['teamId'],
									'spell1Id': summonerSpellKey(sum_spell_json, k['spell1Id']),
									'spell2Id': summonerSpellKey(sum_spell_json, k['spell2Id']),
									'win': participant_team['win'],
									'kills': k['stats']['kills'],
									'deaths': k['stats']['deaths'],
									'assists': k['stats']['assists'],
									'dragonKills': participant_team['dragonKills'],
									'baronKills': participant_team['baronKills'],
									'riftHeraldKills': participant_team['riftHeraldKills'],
									'totalDamageDealtToChampions': k['stats']['totalDamageDealtToChampions'],
									'magicDamageDealtToChampions': k['stats']['magicDamageDealtToChampions'],
									'physicalDamageDealtToChampions': k['stats']['physicalDamageDealtToChampions'],
									'totalDamageTaken': k['stats']['totalDamageTaken'],
									'magicalDamageTaken': k['stats']['magicalDamageTaken'],
									'physicalDamageTaken': k['stats']['physicalDamageTaken'],
									'longestTimeSpentLiving': k['stats']['longestTimeSpentLiving'],
									'visionScore': k['stats']['visionScore'],
									'visionWardsBoughtInGame': k['stats']['visionWardsBoughtInGame'],
									'wardsPlaced': k['stats']['wardsPlaced'],
									'wardsKilled': k['stats']['wardsKilled'],
									'goldEarned': k['stats']['goldEarned'],
									'damageDealtToObjectives': k['stats']['damageDealtToObjectives'],
									'damageDealtToTurrets': k['stats']['damageDealtToTurrets'],
									'firstBloodKill': k['stats']['firstBloodKill'],
									'timeline': k['timeline'],
									'lane': k['timeline']['lane']}
				#push completed array into dict
				match_dict.append(match_data)
	return match_dict

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
						context={"form":form})
	def post(self,request):
		form = SummonerForm(request.POST)
		if form.is_valid():
			text = form.cleaned_data['summonername']
			args = {"form":form, 
					"text": text,
					"mytopfive":top_5_best_champs(text),
					"current_summoner":check_ranked_stats(text),
					"match_data": pull_out_match_data(text)
					}
			return render(request,self.template_name, args)	



