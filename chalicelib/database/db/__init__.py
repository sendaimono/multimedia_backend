# -*- coding: utf-8 -*-
'''
Implementation of TableauDB tables

..codeauthor Mikołaj Kowal <mikolaj.kowal@nftlearning.com>
'''
import enum
import warnings

from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.types import Enum
from sqlalchemy.exc import SAWarning

from chalicelib.database.db import database as db

warnings.filterwarnings(
    'ignore',
    r'.*support Decimal objects natively.*',
    SAWarning,
    r'^sqlalchemy\.sql\.sqltypes$')


def Session():
    return db.session()()


class User(db.Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    uuid = Column(String, nullable=False)
    login = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)