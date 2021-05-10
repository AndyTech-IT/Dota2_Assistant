from django.shortcuts import render
from django.http import HttpResponse

import requests
import datetime
import json

from match_history.models import Hero, Item

# Enter you steam dev code hire
code : str = ""
account_id : str = '196716841'

if (code == ""):
	raise Exception('Empty dev code!!')

Matches_Detail = {}
Matches = None
Heroes = None
Items = None
Yield_Detail_Process = None

class Player_Data:
	Hero_ID = 0
	Hero_Image_Path = None
	Hero_Name = None
	Kills = 0
	Assists = 0
	Deaths = 0
	Last_Hits = 0
	Denies = 0
	Gold_Per_Min = 0
	Xp_Per_Min = 0
	Level = 0
	Hero_Damage = 0
	Tower_Damage = 0
	Hero_Healing = 0
	Gold_Spent = 0

	Items_Images_Paths = []

	def __init__(self, data):
		self.Hero_ID = data['hero_id']
		self.Items_Images_Paths = list()

		self.Kills = data['kills']
		self.Assists = data['assists']
		self.Deaths = data['deaths']
		self.Last_Hits = data['last_hits']
		self.Denies = data['denies']
		self.Gold_Per_Min = data['gold_per_min']
		self.Xp_Per_Min = data['xp_per_min']
		self.Level = data['level']
		self.Hero_Damage = data['hero_damage']
		self.Tower_Damage = data['tower_damage']
		self.Hero_Healing = data['hero_healing']
		self.Gold_Spent = data['gold_spent']

		hero = next(x for x in Heroes if x['id'] == self.Hero_ID)
		hero_name = hero['name'].partition('npc_dota_hero_')[2]
		self.Hero_Image_Path = f'http://cdn.dota2.com/apps/dota2/images/heroes/{hero_name}_full.png'
		self.Hero_Name = hero['localized_name']

		items_id_list = [
			data['item_0'],
			data['item_1'],
			data['item_2'],
			data['item_3'],
			data['item_4'],
			data['item_5'],
			data['backpack_0'],
			data['backpack_1'],
			data['backpack_2'],
			data['item_neutral']
		]
		for id in items_id_list:
			if (id != 0):
				item = next(i for i in Items if i['id'] == id)
				item_name : str = item['name'].partition('item_')[2]
				if (item_name.startswith('recipe')):
					self.Items_Images_Paths.append(f'http://cdn.dota2.com/apps/dota2/images/items/recipe_lg.png')
				else:
					self.Items_Images_Paths.append(f'http://cdn.dota2.com/apps/dota2/images/items/{item_name}_lg.png')
			else:
				self.Items_Images_Paths.append(f'https://dummyimage.com/85x64/222.jpg&text=%20')
			
		pass

class Match_Data:
	Radiant_Is_Victory = True
	Duration = '00:00'
	Start_Date_Time = "01.01.2000 00:00:00"
	Radiant_Players = None
	Dire_Players = None

	def __init__(self, match_detail):

		self.Radiant_Players = list()
		self.Dire_Players = list()
		self.Radiant_Is_Victory = match_detail['radiant_win']
		duration_in_sec = match_detail['duration']
		sec = duration_in_sec % 60
		min = (duration_in_sec - sec) // 60
		hours = (duration_in_sec - sec) % 60
		self.Duration = f'{hours}:{min}:{sec}' if hours>0 else f'{min}:{sec}'
		timestamp = match_detail['start_time']
		date_time = datetime.datetime.fromtimestamp(timestamp)
		self.Start_Date_Time = date_time.strftime('%d.%m.%Y %H:%M:%S')

		players = match_detail['players']
		for data in players[:5:]:
			self.Radiant_Players.append(Player_Data(data))
		for data in players[5::]:
			self.Dire_Players.append(Player_Data(data))
		pass

def Get_Match_History_Data():
	URL : str = 'http://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/v1'
	params = {'key': code, 'account_id': account_id}
	result : str = requests.get(URL, params=params)
	return result.text

def Parce_Match_History_Data(data:str):
	History = json.loads(data)
	return History['result']['matches']

def Get_Match_Detail_Data(id):
	URL : str = 'http://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v1'
	params = { 'key':code, 'match_id':id }
	result : str = requests.get(URL, params=params)
	return result.text

def Parce_Match_Detail_Data(data):
	detail = json.loads(data)
	return detail['result']

def Get_Matches_Detail(matches):
	result_dict: dict = dict()
	for match in matches:
		id = match['match_id']
		detail_data = Get_Match_Detail_Data(id)
		match_detail = Parce_Match_Detail_Data(detail_data)
		result = Match_Data(match_detail)
		result_dict.update({id: result})
	return result_dict

def Get_Heroes():
	URL : str = 'http://api.steampowered.com/IEconDOTA2_570/GetHeroes/v1'
	language='ru'
	params = {'key':code, 'language':language }

	result = requests.get(URL, params=params)
	data = json.loads(result.text)['result']['heroes']

	return data

def Get_Items():

	URL : str = 'http://api.steampowered.com/IEconDOTA2_570/GetGameItems/v1'
	language='ru'
	params = {'key':code, 'language':language }
	
	result = requests.get(URL, params=params)
	data = json.loads(result.text)['result']['items']

	return data

def Update_Hereos(request):
	Hero.objects.all().delete()
	for hero in Get_Heroes():
		name = hero["localized_name"]
		h = Hero.objects.create(Data = hero, Name=name)
	return HttpResponse('Successfull update')

def Update_Items(request):
	Item.objects.all().delete()
	for item in Get_Items():
		i = Item.objects.create(Data = item)
	return HttpResponse('Successfull update')

def GetMatches(request, page_number):
	matches_on_page = 5
	global Matches, Matches_Detail, Heroes, Items
	if (Matches is None):
		Matches_Detail = {}
		data : str = Get_Match_History_Data()
		Matches = Parce_Match_History_Data(data)

		Heroes = [ hero.Data for hero in Hero.objects.all() ]
		Items = [ item.Data for item in Item.objects.all() ]
		
	
	start_index = matches_on_page*(page_number-1)
	end_index = matches_on_page*page_number
	Matches_Detail = Get_Matches_Detail(Matches[start_index:end_index])

	min_page_num = 1
	previous_page_num = page_number - min_page_num if page_number > min_page_num else min_page_num
	max_page_num = len(Matches)//matches_on_page
	next_page_num = page_number + 1 if page_number < max_page_num else max_page_num

	pages = [num for num in range(page_number-4, page_number+4+1) if min_page_num <= num <= max_page_num]
	
	data_dict = {
		'Matches_Detail': Matches_Detail, 
		'page_number': page_number, 
		'previous_page_num': previous_page_num, 
		'min_page_num': min_page_num,
		'max_page_num': max_page_num, 
		'next_page_num': next_page_num,
		'pages': pages,
			  }

	return render(request, 'match_history/Maches.html', data_dict)