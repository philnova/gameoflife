from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Boolean
import arrow

Base = declarative_base()

class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    google_id = Column(String(200), nullable=False)


    def __init__(self, name, google_id):
        self.name = name
        self.google_id = google_id

class Board(Base):

    __tablename__ = 'boards'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    nickname = Column(String(200), nullable=False)
    xdim = Column(Integer, nullable=False) #x dimension
    ydim = Column(Integer, nullable=False) #y dimension
    seed = Column(String(500000), nullable=False)
    rules = Column(String(20), nullable=False)
    shared = Column(Boolean, default=True)



    def __init__(self, user_id, nickname, xdim, ydim, seed, rules, shared):
        self.user_id = user_id
        self.nickname = nickname
        self.xdim = xdim
        self.ydim = ydim
        self.seed = seed
        self.rules = rules
        self.shared = shared

class Rating(Base):

    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    board_id = Column(Integer, ForeignKey('boards.id'))
    like = Column(Boolean)

    def __init__(self, user_id, board_id, like):
        self.user_id = user_id
        self.board_id = board_id
        self.like = like


