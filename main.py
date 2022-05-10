import sys

import requests
from csv import DictReader
from ast import literal_eval

import re
# pprint library is used to make the output look more pretty
from pprint import pprint
from html import escape
from howlongtobeatpy import HowLongToBeat
from hltb import hltb
from base import Session, engine, Base
from schema import User, Game, Genre, UserGames, Platform, Perspective, Website
from sqlalchemy.dialects.postgresql import insert

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
    s = s.strip().replace('™', '').replace('®', '').replace('"', "'")
    for rx in clean.rx:
        s = rx[0].sub(rx[1], s)
    return escape(s) if bPurge else s


def get_howlongtobeat_infos(search):
    pprint('how long to beat')
    result = HowLongToBeat().search(search)
    if result:
        return {
            "howlongtobeat_url": result[0].game_web_link,
            "howlongtobeat_main": float(str(result[0].gameplay_main).replace("½", ".5")),
            "howlongtobeat_main_unit": result[0].gameplay_main_unit,
            "howlongtobeat_main_extra": float(str(result[0].gameplay_main_extra).replace("½", ".5")),
            "howlongtobeat_main_extra_unit": result[0].gameplay_main_extra_unit,
            "howlongtobeat_completionist": float(str(result[0].gameplay_completionist).replace("½", ".5")),
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

webs = ['official', 'wikia', 'wikipedia', 'facebook', 'twitter', 'twitch', '', 'instagram', 'youtube', 'iphone', 'ipad',
        'android', 'steam', 'reddit', 'itch', 'epicgames', 'gog', 'discord']

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
            row['title'] = clean(re.sub(i[0], i[1], row['title']), bPurge=False)
        plist = literal_eval(row['platformList']) if row['platformList'] else []

        pprint(row['title'])
        game_db = session.query(Game).filter(Game.name == row['title']).first()
        if game_db:
            pprint('salto db')
            continue

        body = 'fields name,aggregated_rating,aggregated_rating_count,total_rating,total_rating_count,cover.*,genres.name,genres.slug,player_perspectives.name,player_perspectives.slug,themes.name,platforms.name,platforms.slug,platforms.platform_logo.url,slug,summary,storyline,websites.category,websites.url,url,similar_games,version_parent,version_title;where name = "%s";' % \
               row['title']
        response = requests.post("https://api.igdb.com/v4/games", data=body.encode('utf-8'), headers=headers)
        game = response.json()

        # pprint(game)

        if len(game) > 0:
            game_db = session.query(Game).filter(Game.igdb_id == game[0]['id']).first()

            if game_db:
                pprint('salto')
                if game_db.users:
                    for game_user in game_db.users:
                        if game_user.user_id != user.id and game_user.game_id != game_db.id:
                            user_game = UserGames(user=user, game=game_db, platforms=plist)
                            session.add(user_game)
                else:
                    user_game = UserGames(user=user, game=game_db, platforms=plist)
                    session.add(user_game)
                continue

            game[0]['igdb_id'] = game[0]['id']
            pprint(game[0]['name'])
            pprint(game[0]['igdb_id'])
            # game[0]['platform_list'] = literal_eval(row['platformList']) if row['platformList'] else []
            del game[0]['id']
            howlongtobeat_infos = get_howlongtobeat_infos(game[0]['name'])

            game[0]['aggregated_rating'] = game[0]['aggregated_rating'] if 'aggregated_rating' in game[0] else None
            game[0]['aggregated_rating_count'] = game[0]['aggregated_rating_count'] if 'aggregated_rating_count' in game[0] else None
            game[0]['total_rating'] = game[0]['total_rating'] if 'total_rating' in game[0] else None
            game[0]['total_rating_count'] = game[0]['total_rating_count'] if 'total_rating_count' in game[0] else None
            game[0]['howlongtobeat_rating'] = hltb(howlongtobeat_infos['howlongtobeat_url']) if howlongtobeat_infos else None
            game[0]['howlongtobeat_infos'] = howlongtobeat_infos
            pprint(game[0]['howlongtobeat_rating'])

            game_db = Game(**game[0])

            if 'genres' in game[0]:
                genres = []
                for genre in game[0]['genres']:
                    gen = session.query(Genre).filter(Genre.id == genre['id']).first()
                    if not gen:
                        gen = Genre(**genre)
                        session.add(gen)
                    genres.append(gen)
                game_db.genres = genres

            if 'platforms' in game[0]:
                platforms = []
                for platform in game[0]['platforms']:
                    plat = session.query(Platform).filter(Platform.id == platform['id']).first()
                    platform['logo'] = platform['platform_logo']['url'] if 'platform_logo' in platform else None
                    if not plat:
                        plat = Platform(**platform)
                        session.add(plat)
                    platforms.append(plat)
                game_db.platforms = platforms

            if 'player_perspectives' in game[0]:
                perspectives = []
                for perspective in game[0]['player_perspectives']:
                    perp = session.query(Perspective).filter(Perspective.id == perspective['id']).first()
                    if not perp:
                        perp = Perspective(**perspective)
                        session.add(perp)
                    perspectives.append(perp)
                game_db.perspectives = perspectives

            if 'websites' in game[0]:
                websites = []
                for website in game[0]['websites']:
                    index = int(website['category']) - 1
                    website['category'] = webs[index]
                    web = Website(**website)
                    web.game = game_db
                    session.add(web)
                    websites.append(web)
                game_db.websites = websites

            user_game = UserGames(user=user, game=game_db, platforms=plist)
            session.add(user_game)
            session.add(game_db)
            session.commit()
            # db.games.update_one({'name': game[0]['name']}, {'$set': game[0]}, upsert=True)
            # platform_list = literal_eval(row['platformList']) if row['platformList'] else []
            # db.users.update_one({'_id': user_id, "games.igdb_id": game[0]['igdb_id'] }, {'$set': {'games.$.platforms': platform_list}})
        else:
            pprint('no  found')
session.close()
