import requests
from csv import DictReader
from ast import literal_eval
from html import escape
from html.parser import HTMLParser
import selenium.webdriver

import re
import json
from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
from selenium.webdriver.common.by import By

client = MongoClient('mongodb+srv://test:I3Ki5JzvfQA34C3F@realmcluster.n0xvu.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db=client.games


headers = {
    "Client-ID": "mvbeuf5jy59umly0yk1hzk6i6mqmbk",
    "Authorization": "Bearer aawj8q3mvcedzzzd9zh9ciu531qtue"
}

# body = 'fields name,aggregated_rating,aggregated_rating_count,total_rating,total_rating_count,cover.*,genres.name,player_perspectives.name,themes.name,platforms.name,slug,summary,storyline,websites.category,websites.url,url,similar_games,version_parent,version_title;where name ~ *"mass effect legendary"*;'
#
# response = requests.post("https://api.igdb.com/v4/games", data=body, headers=headers)
# game = response.json()

def clean(s, bPurge=True):
	s = s.strip()
	for rx in clean.rx:
		s = rx[0].sub(rx[1], s)
	return escape(s) if bPurge else s
clean.rx = [
	(re.compile(r'\.\.\.'), '…'),
	(re.compile(r'\s+-\s+'), ' – '),
	(re.compile(r'\u0092'), '’'),  # PU2
	(re.compile(r'\u0093'), '“'),  # STS
	(re.compile(r'\u0094'), '”'),  # CCH
	(re.compile(r'\s*\u0097\s*'), ' – '),  # CCH
]

games = []
titleReplaceList = [
		(r'\.\.\.', '…'),
	]  # Cleans the title

delimeter = '\t'

times = {}

class LinuxHint_Parse(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Start tag:", tag)
        for attr in attrs:
            times[attr[0]] = attr[1]

    def handle_endtag(self, tag):
        print("End tag :", tag)

    def handle_data(self, data):
        print("Data :", data)

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
            print("Num ent :", c)

    def handle_decl(self, data):
        print("Decl :", data)


parser = LinuxHint_Parse()


# Set URL value
# crl.setopt(crl.URL, 'https://howlongtobeat.com/game.php?id=1')
url = 'https://howlongtobeat.com/game.php?id=1'
# r = requests.get(url, headers={"User-Agent": "AugmentedSteam/1.0 (+bots@isthereanydeal.com)"})

driver = selenium.webdriver.Chrome()

driver.get('https://howlongtobeat.com/game.php?id=1')

platformNodes = driver.find_elements_by_xpath("//table[@class='game_main_table']//td[1]/text()[contains(., 'Platform')]/..")
for platformNode in platformNodes:
    headNodes = platformNode.find_elements_by_xpath("ancestor::tr//td")
    pprint(headNodes)

# with open('./gameDB.csv', 'r', encoding='utf-8', newline='') as csvfile:
#     for row in DictReader(csvfile, delimiter='\t'):
#
#
#         # Fix common problems with titles
#         for i in titleReplaceList:
#             row['title'] = clean(re.sub(i[0], i[1], row['title']))
#
#         pprint(row['title'])
#
#         body = 'fields name,aggregated_rating,aggregated_rating_count,total_rating,total_rating_count,cover.*,genres.name,player_perspectives.name,themes.name,platforms.name,slug,summary,storyline,websites.category,websites.url,url,similar_games,version_parent,version_title;where name ~ *"%s"*;' % row['title']
#         response = requests.post("https://api.igdb.com/v4/games", data=body.encode('utf-8'), headers=headers)
#         game = response.json()
#
#         if (len(game) == 1):
#             game[0]['igdb_id'] = game[0]['id']
#             game[0]['platform_list'] = literal_eval(row['platformList']) if row['platformList'] else []
#             del game[0]['id']
#             db.games.update_one({'name': game[0]['name']}, {'$set': game[0]}, upsert=True)
