from django import forms

class SummonerForm(forms.Form):
	summonername = forms.CharField(label="Insert Summoner Name")