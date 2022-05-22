from sqlalchemy import Column, ForeignKey, Integer, String, Table, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSON, ENUM
from base import Base

genres_games = Table(
    'genres_games',
    Base.metadata,
    Column('game_id', ForeignKey('games.id'), primary_key=True),
    Column('genre_id', ForeignKey('genres.id'), primary_key=True)
)

platforms_games = Table(
    'platforms_games',
    Base.metadata,
    Column('game_id', ForeignKey('games.id'), primary_key=True),
    Column('platform_id', ForeignKey('platforms.id'), primary_key=True)
)

perspectives_games = Table(
    'perspectives_games',
    Base.metadata,
    Column('game_id', ForeignKey('games.id'), primary_key=True),
    Column('perspective_id', ForeignKey('perspectives.id'), primary_key=True)
)

webs = ['official', 'wikia', 'wikipedia', 'facebook', 'twitter', 'twitch', '', 'instagram', 'youtube', 'iphone', 'ipad',
        'android', 'steam', 'reddit', 'itch', 'epicgames', 'gog', 'discord']


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    email = Column(String)
    games = relationship('UserGames', back_populates='user')


class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True, autoincrement=True)
    igdb_id = Column(Integer, nullable=False, unique=True)
    title = Column(String, nullable=False)
    slug = Column(String)
    summary = Column(String, nullable=True)
    similar_games = Column(ARRAY(Integer), nullable=True)
    release_date = Column(Date, nullable=True)
    url = Column(String, nullable=True)
    storyline = Column(String, nullable=True)
    cover = Column(String, nullable=True)
    igdb_cover = Column(String, nullable=True)
    background = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    critic = Column(Float, nullable=True)
    duration = Column(Float, nullable=True)
    howlongtobeat_infos = Column(JSON, nullable=True)
    websites = relationship('Website')
    genres = relationship('Genre', secondary=genres_games, backref='games')
    platforms = relationship('Platform', secondary=platforms_games, backref='games')
    perspectives = relationship('Perspective', secondary=perspectives_games, backref='games')
    users = relationship('UserGames', back_populates='game')

    def __init__(self, **kwargs):
        self.igdb_id = kwargs['igdb_id']
        self.title = kwargs['title']
        self.slug = kwargs['slug']
        self.summary = kwargs['summary']
        self.similar_games = kwargs['similar_games']
        self.url = kwargs['url']
        self.cover = kwargs['cover']
        self.igdb_cover = kwargs['igdb_cover']
        self.rating = kwargs['rating']
        self.critic = kwargs['critic']
        self.storyline = kwargs['storyline']
        self.background = kwargs['background']
        self.release_date = kwargs['release_date']
        self.howlongtobeat_infos = kwargs['howlongtobeat_infos']
        self.duration = kwargs['duration']


class UserGames(Base):
    __tablename__ = 'users_games'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'), primary_key=True)
    platforms = Column(ARRAY(String))
    user = relationship(User, back_populates='games')
    game = relationship(Game, back_populates='users')


class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.name = kwargs['name']
        self.slug = kwargs['slug']


class Platform(Base):
    __tablename__ = 'platforms'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    logo = Column(String, nullable=True)

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.name = kwargs['name']
        self.slug = kwargs['slug']
        self.logo = kwargs['platform_logo']['url'] if 'platform_logo' in kwargs else None


class Perspective(Base):
    __tablename__ = 'perspectives'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.name = kwargs['name']
        self.slug = kwargs['slug']


class Website(Base):
    __tablename__ = 'websites'
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    category = Column(
        ENUM('official', 'wikia', 'wikipedia', 'facebook', 'twitter', 'twitch', 'instagram', 'youtube', 'iphone',
             'ipad', 'android', 'steam', 'reddit', 'itch', 'epicgames', 'gog', 'discord', name='category_names'))
    game_id = Column(Integer, ForeignKey('games.id'))

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.url = kwargs['url']
        index = int(kwargs['category']) - 1
        self.category = webs[index]
