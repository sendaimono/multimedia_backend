# -*- coding: utf-8 -*-
'''
Implementation of TableauDB tables

..codeauthor Mikołaj Kowal <mikolaj.kowal@nftlearning.com>
'''
import enum
import warnings

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey
from sqlalchemy.types import Enum
from sqlalchemy.exc import SAWarning
from sqlalchemy.orm import relationship

from chalicelib.database.db import database

warnings.filterwarnings(
    'ignore',
    r'.*support Decimal objects natively.*',
    SAWarning,
    r'^sqlalchemy\.sql\.sqltypes$')


def Session():
    return database.session()()


class User(database.Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    uuid = Column(String, nullable=False)
    login = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    messages = relationship("Message")
    rooms = relationship("Room")

class Room(database.Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True)
    room_gid = Column(String, nullable=False)
    owner = Column(Integer, ForeignKey('users.id'))
    created = Column(DateTime, nullable=False)
    messages = relationship("Message")

class Message(database.Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    room = Column(Integer, ForeignKey('rooms.id'))
    sender = Column(Integer, ForeignKey('users.id'))
    created = Column(DateTime, nullable=False)
    msg = Column(String, nullable=False)