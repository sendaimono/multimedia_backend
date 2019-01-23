import socket
from threading import Thread, Event, Lock
import logging as log
from typing import Tuple, List
from chalicelib.database.db import User, Room
import json

CONNNECTION = Tuple[str, int]


class Client():
    sid: str = None
    user: User = None
    room: Room = None
    isDead = False

    def __init__(self, sid):
        self.sid = sid
    

    def verify(self, msg: str):
        from chalicelib.validator import validate
        from chalicelib.room import get_room_by_room_gid
        try:
            data = json.loads(msg)
        except Exception as e:
            log.error(e)
            return False
        self.user = validate(data.get('uuid'))
        self.room = get_room_by_room_gid(data.get('room_gid'))
        if not self.user or not self.room:
            return False
        return True