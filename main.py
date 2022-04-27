import requests
from csv import DictReader
from ast import literal_eval

import re
import json
from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
from html import escape
from howlongtobeatpy import HowLongToBeat
from hltb import hltb
from base import Session, engine, Base
from schema import User, Game

Base.metadata.create_all(engine)
session = Session()

headers = {
    "Client-ID": "mvbeuf5jy59umly0yk1hzk6i6mqmbk",
    "Authorization": "Bearer aawj8q3mvcedzzzd9zh9ciu531qtue"
}


user_id = '625aed40c46cda3ded989a0f'

# body = 'fields name,aggregated_rating,aggregated_rating_count,total_rating,total_rating_count,cover.*,genres.name,player_perspectives.name,themes.name,platforms.name,slug,summary,storyline,websites.category,websites.url,url,similar_games,version_parent,version_title;where name ~ *"mass effect legendary"*;'
#
# response = requests.post("https://api.igdb.com/v4/games", data=body, headers=headers)
# game = response.json()

def clean(s, bPurge=True):
    s = s.strip()
    for rx in clean.rx:
        s = rx[0].sub(rx[1], s)
    return escape(s) if bPurge else s


def get_howlongtobeat_infos(search):
    result = HowLongToBeat().search(search)
    if result:
        return {
            "howlongtobeat_url": result[0].game_web_link,
            "howlongtobeat_main": result[0].gameplay_main.replace("½", ".5"),
            "howlongtobeat_main_unit": result[0].gameplay_main_unit,
            "howlongtobeat_main_extra": result[0].gameplay_main_extra.replace("½", ".5"),
            "howlongtobeat_main_extra_unit": result[0].gameplay_main_extra_unit,
            "howlongtobeat_completionist": result[0].gameplay_completionist.replace("½", ".5"),
            "howlongtobeat_completionist_unit": result[0].gameplay_completionist_unit,
        }
    return None


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


# graphql_headers = {
#     'content-type': 'application/json',
#     'x-hasura-admin-secret': 'iuK7iytI8c3t3qphXD6G5kdsEw3aP06gicJUuh1FViAHKaQMypegSmbuBDRUQ1M1'
# }
#
# body = '''query get_users {
#     games_users {
#     id
#     name
#   }
# }'''
#
# p = requests.post('https://viable-hedgehog-12.hasura.app/v1/graphql', json={'query': body}, headers=graphql_headers)
# pprint(p.json())


user = session.query(User).filter(User.name == 'Simone').first()
pprint(user.name)

with open('./gameDB.csv', 'r', encoding='utf-8', newline='') as csvfile:
    for row in DictReader(csvfile, delimiter='\t'):
        # Fix common problems with titles
        for i in titleReplaceList:
            row['title'] = clean(re.sub(i[0], i[1], row['title']))
        pprint(row['title'])

        body = 'fields name,aggregated_rating,aggregated_rating_count,total_rating,total_rating_count,cover.*,genres.name,player_perspectives.name,themes.name,platforms.name,slug,summary,storyline,websites.category,websites.url,url,similar_games,version_parent,version_title;where name = "%s";' % \
               row['title']
        response = requests.post("https://api.igdb.com/v4/games", data=body.encode('utf-8'), headers=headers)
        game = response.json()

        if len(game) == 1:
            game[0]['igdb_id'] = game[0]['id']
            pprint(game[0]['igdb_id'])
            # game[0]['platform_list'] = literal_eval(row['platformList']) if row['platformList'] else []
            del game[0]['id']
            howlongtobeat_infos = get_howlongtobeat_infos(game[0]['name'])

            game[0]['howlongtobeat_rating'] = hltb(howlongtobeat_infos['howlongtobeat_url'])
            game[0]['howlongtobeat_infos'] = howlongtobeat_infos
            # pprint(game[0])

            game_db = Game(game[0]['igdb_id'], game[0]['name'], game[0]['slug'], game[0]['summary'])
            game_db.users = [user]
            session.add(game_db)

            # db.games.update_one({'name': game[0]['name']}, {'$set': game[0]}, upsert=True)
            # platform_list = literal_eval(row['platformList']) if row['platformList'] else []
            # db.users.update_one({'_id': user_id, "games.igdb_id": game[0]['igdb_id'] }, {'$set': {'games.$.platforms': platform_list}})
session.commit()
session.close()
