import socket
from threading import Thread, Event, Lock
import logging as log
from typing import Tuple, List
from chalicelib.database.db import User, Room
import json
from uuid import uuid1
from chalicelib.chat_event import ChatEvent

CONNNECTION = Tuple[str, int]


class Client(Thread):
    socket: socket.socket
    connection: CONNNECTION
    user: User
    room: Room
    connection_uuid: str
    _event: Event
    chat_events: List[ChatEvent]
    _lock: Lock

    def __init__(self, s: socket.socket, c: CONNNECTION):
        Thread.__init__(self)
        self.chat_events = []
        self.socket = s
        self.connection = c
        self.connection_uuid = str(uuid1())
        self._event = Event()
        self._event.clear()
        self._lock = Lock()

    def add_event(self, event: ChatEvent):
        self._lock.acquire()
        self.chat_events.append(event)
        self._lock.release()
        log.debug("Added event")
        self._event.set()

    def get_event(self) -> ChatEvent:
        self._lock.acquire()
        try:
            return self.chat_events.pop(0)
        except:
            return None
        finally:
            self._lock.release()

    def read(self) -> bytes:
        data = []
        while True:
            try:
                log.debug("Reading chunk...")
                recv = self.socket.recv(1024)
                log.debug("Read chunk...")
            except Exception as e:
                log.error(e)
                recv = None
            if recv:
                data.append(recv)
            if len(recv) < 1024:
                break
            else:
                break
        return b''.join(data)

    def send(self, msg: str) -> bool:
        try:
            data = msg.encode()
            self.socket.sendall(data)
            return True
        except Exception as e:
            log.error(f'User {self.user.uuid}: {e}')
        return False

    def run(self):
        log.debug(f'User {self.user.login}:{self.user.uuid} connected to room '
                  f'{self.room.room_gid}!')
        while True:
            log.debug("Going sleep (client)!")
            self._event.wait()
            log.debug("Received event!")
            while len(self.chat_events):
                event: ChatEvent = self.get_event()
                if event:
                    self.process_event(event)
            self._event.clear()

    def process_event(self, event: ChatEvent):
        if (self.room.room_gid == event.room_gid and
                self.user.uuid != event.user_uuid):
            log.debug(f"Sending msg to {self.user.uuid}...")
            res = self.send(json.dumps(event.to_json()))
            log.debug(f"Sending msg to {self.user.uuid}: {res}")

