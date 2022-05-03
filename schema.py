from sqlalchemy import Column, ForeignKey, Integer, String, Table, Float
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
    name = Column(String, nullable=False)
    slug = Column(String)
    summary = Column(String)
    similar_games = Column(ARRAY(Integer))
    url = Column(String)
    cover = Column(JSON)
    aggregated_rating = Column(Float)
    aggregated_rating_count = Column(Integer)
    total_rating = Column(Float)
    total_rating_count = Column(Integer)
    howlongtobeat_rating = Column(Integer)
    howlongtobeat_infos = Column(JSON)
    websites = relationship('Website')
    genres = relationship('Genre', secondary=genres_games, backref='games')
    platforms = relationship('Platform', secondary=platforms_games, backref='games')
    perspectives = relationship('Perspective', secondary=perspectives_games, backref='games')
    users = relationship('UserGames', back_populates='game')

    def __init__(self, **kwargs):
        self.igdb_id = kwargs['igdb_id']
        self.name = kwargs['name']
        self.slug = kwargs['slug']
        self.summary = kwargs['summary']
        self.similar_games = kwargs['similar_games']
        self.url = kwargs['url']
        self.cover = kwargs['cover']
        self.aggregated_rating = kwargs['aggregated_rating']
        self.aggregated_rating_count = kwargs['aggregated_rating_count']
        self.total_rating = kwargs['total_rating']
        self.total_rating_count = kwargs['total_rating_count']
        self.howlongtobeat_rating = kwargs['howlongtobeat_rating']
        self.howlongtobeat_infos = kwargs['howlongtobeat_infos']


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
    logo = Column(String)

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.name = kwargs['name']
        self.slug = kwargs['slug']
        self.logo = kwargs['logo']


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
        self.category = kwargs['category']
