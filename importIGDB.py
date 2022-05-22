from ast import literal_eval
import requests
from hltb import get_howlongtobeat_infos, hltb
from datetime import date
from schema import Game, UserGames, Genre, Platform, Perspective, Website

headers = {
    "Client-ID": "mvbeuf5jy59umly0yk1hzk6i6mqmbk",
    "Authorization": "Bearer aawj8q3mvcedzzzd9zh9ciu531qtue"
}


def set_relation(Relation, items, session):
    relations = []
    for item in items:
        el = session.query(Relation).filter(Relation.id == item['id']).first()
        if not el:
            el = Relation(**item)
            session.add(el)
        relations.append(el)
    return relations


def import_igdb(row, user, session):
    plist = literal_eval(row['platformList']) if row['platformList'] else []
    body = 'fields name,aggregated_rating,rating,cover.image_id,genres.name,genres.slug,first_release_date,' \
           'player_perspectives.name,player_perspectives.slug,themes.name,platforms.name,platforms.slug,' \
           'platforms.platform_logo.url,slug,summary,storyline,websites.category,websites.url,url,similar_games;' \
           'sort aggregated_rating desc; where name = "%s";' % row['title']
    # pprint(body)
    response = requests.post("https://api.igdb.com/v4/games", data=body.encode('utf-8'), headers=headers)
    games = response.json()

    game_db = None

    if len(games) > 0:
        game_db = session.query(Game).filter(Game.igdb_id == games[0]['id']).first()

        if game_db:
            if game_db.users:
                for game_user in game_db.users:
                    if game_user.user_id != user.id and game_user.game_id != game_db.id:
                        user_game = UserGames(user=user, game=game_db, platforms=plist)
                        session.add(user_game)
            else:
                user_game = UserGames(user=user, game=game_db, platforms=plist)
                session.add(user_game)
            return game_db

        if not game_db:
            game = {'title': row['title'], 'igdb_id': games[0]['id'], 'slug': games[0]['slug'],
                    'summary': games[0]['summary'] if 'summary' in games[0] else row['summary'],
                    'url': games[0]['url'], 'storyline': games[0]['storyline'] if 'storyline' in games[0] else None,
                    'background': row['backgroundImage'], 'cover': row['verticalCover'],
                    'igdb_cover': '//images.igdb.com/igdb/image/upload/t_cover_big/nocover.png',
                    'release_date': date.fromisoformat(row['releaseDate']) if row['releaseDate'] != '' else date.fromtimestamp(games[0]['first_release_date'])}

            if 'cover' in games[0]:
                game['igdb_cover'] = '//images.igdb.com/igdb/image/upload/t_cover_big/%s.jpg' % games[0]["cover"][
                    "image_id"]

            game['similar_games'] = games[0]['similar_games'] if 'similar_games' in games[0] else []

            howlongtobeat_infos = get_howlongtobeat_infos(row['title'])
            print('return hltb')
            print(howlongtobeat_infos)
            game['howlongtobeat_infos'] = howlongtobeat_infos

            duration = None
            if howlongtobeat_infos:
                if howlongtobeat_infos.howlongtobeat_infos.howlongtobeat_main_extra != -1:
                    unit = 60 if howlongtobeat_infos.howlongtobeat_main_extra_unit == 'Hours' else 1
                    duration = howlongtobeat_infos.howlongtobeat_infos.howlongtobeat_main_extra * unit
                else :
                    unit = 60 if howlongtobeat_infos.howlongtobeat_main_unit == 'Hours' else 1
                    duration = howlongtobeat_infos.howlongtobeat_infos.howlongtobeat_main * unit

            print(duration)
            game['duration'] = duration
            game['rating'] = round(games[0]['rating']) if 'rating' in games[0] else hltb(
                howlongtobeat_infos['howlongtobeat_url']) if howlongtobeat_infos else None
            game['critic'] = row['criticsScore'] if row['criticsScore'] != '' else round(
                games[0]['aggregated_rating']) if 'aggregated_rating' in games[0] else None

            game_db = Game(**game)

            if 'genres' in games[0]:
                game_db.genres = set_relation(Genre, games[0]['genres'], session)

            if 'platforms' in games[0]:
                game_db.platforms = set_relation(Platform, games[0]['platforms'], session)

            if 'player_perspectives' in games[0]:
                game_db.perspectives = set_relation(Perspective, games[0]['player_perspectives'], session)

            if 'websites' in games[0]:
                game_db.websites = set_relation(Website, games[0]['websites'], session)

            user_game = UserGames(user=user, game=game_db, platforms=plist)
            session.add(user_game)
            session.add(game_db)
            session.commit()

    return game_db
