from threading import Thread, Lock, Event
from chalicelib.socket.client import Client
from typing import List
from chalicelib.chat_event import ChatEvent, EventType
import logging as log
import json
from flask_socketio import SocketIO
from flask import Flask, request


class Signal:
    worker: Thread
    events: List[ChatEvent] = []
    clients: List[Client] = []
    events_lock: Lock
    client_lock: Lock
    events_emmitter: Event
    io: SocketIO = None

    @staticmethod
    def add_client(client: Client):
        try:
            Signal.client_lock.acquire()
            Signal.clients.append(client)
            Signal.add_event(
                ChatEvent(client.room.room_gid,
                          EventType.JOIN_ROOM,
                          {
                              'user': client.user.username
                          }))
            Signal.events_emmitter.set()
        finally:
            Signal.client_lock.release()

    @staticmethod
    def add_event(event: ChatEvent):
        Signal.events_lock.acquire()
        Signal.events.append(event)
        Signal.events_lock.release()

    @staticmethod
    def remove_client(sid: str):
        try:
            Signal.client_lock.acquire()
            for idx, c in enumerate(Signal.clients):
                if c.sid == sid:
                    Signal.clients.pop(idx)
                    log.debug(
                        f'\nClient: {c.user.username}\n'
                        f'room_gid: {c.room.room_gid}\n'
                        'disconnected')
                    Signal.add_event(
                        ChatEvent(c.room.room_gid,
                                  EventType.LEAVE_ROOM,
                                  {
                                      'user': c.user.username
                                  }))
                    Signal.events_emmitter.set()
        finally:
            Signal.client_lock.release()

    @staticmethod
    def already_connected(cli: Client) -> bool:
        try:
            Signal.client_lock.acquire()
            for c in Signal.clients:
                log.debug(c.room.room_gid)
                log.debug(cli.room.room_gid)
                log.debug(c.user.uuid)
                log.debug(cli.user.uuid)
                if(c.user.uuid == cli.user.uuid and
                        c.room.room_gid == cli.room.room_gid):
                    return True
            return False
        finally:
            Signal.client_lock.release()

    @staticmethod
    def get_event() -> ChatEvent:
        Signal.events_lock.acquire()
        try:
            return Signal.events.pop(0)
        except:
            return None
        finally:
            Signal.events_lock.release()

    @staticmethod
    def share_event(event: ChatEvent):
        try:
            Signal.client_lock.acquire()
            for c in Signal.clients:
                if c.room.room_gid == event.room_gid:
                    log.debug(f'Emitting {event.event_type} to {c.sid}')
                    Signal.io.emit(
                        event.event_type,
                        event.data,
                        room=c.sid)
        finally:
            Signal.client_lock.release()

    @staticmethod
    def run():
        log.info("Signal thread started!")
        while True:
            Signal.events_emmitter.wait()
            log.info("Recevied event to emmit")
            log.debug(Signal.io)
            if Signal.io is not None:
                while len(Signal.events):
                    event: ChatEvent = Signal.get_event()
                    log.info('Preparing to send')
                    if event:
                        # log.debug(f"Event: {json.dumps(event.data)}")
                        Signal.share_event(event)
            log.debug("Going to sleep...")
            Signal.events_emmitter.clear()


def init(io: SocketIO):
    log.debug("Initing Signal...")
    Signal.io = io
    Signal.events_lock = Lock()
    Signal.client_lock = Lock()
    Signal.events_emmitter = Event()
    Signal.events_emmitter.clear()
    Signal.worker = Thread(target=Signal.run)
    Signal.worker.start()


def emmit(event: ChatEvent):
    Signal.add_event(event)
    Signal.events_emmitter.set()
    # emit('test', {'kk': 'asdf'}, room=sids[-2])
