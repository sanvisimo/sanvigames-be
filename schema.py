from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import relationship
from base import Base

user_games_association = Table('games_users', Base.metadata,
    Column('game_id', ForeignKey('games.id')),
    Column('user_id', ForeignKey('users.id'))
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    email = Column(String)
    games = relationship("Game", secondary=user_games_association)


class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, autoincrement=True)
    igdb_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    slug = Column(String)
    summary = Column(String)
    games = relationship("User", secondary=user_games_association)

    def __init__(self, igdb_id, name, slug, summary):
        self.igdb_id = igdb_id
        self.name = name
        self.slug = slug
        self.summary = summary
