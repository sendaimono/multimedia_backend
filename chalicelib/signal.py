from threading import Thread, Lock, Event
from chalicelib.socket.client import Client
from typing import List
from chalicelib.chat_event import ChatEvent
import logging as log
import json

class Signal:
    worker: Thread
    events: List[ChatEvent] = []
    clients: List[Client] = []
    events_lock: Lock
    events_emmitter: Event

    @staticmethod
    def add_client(client: Client):
        Signal.clients.append(client)

    @staticmethod
    def add_event(event: ChatEvent):
        Signal.events_lock.acquire()
        Signal.events.append(event)
        Signal.events_lock.release()

    @staticmethod
    def remove_client(connection_uuid: str):
        for idx, c in enumerate(Signal.clients):
            if c.connection_uuid == connection_uuid:
                Signal.clients.pop(idx)
                log.debug(f'Client id: {connection_uuid} disconnected')

    @staticmethod
    def already_connected(user_uuid: str, room_gid: str) -> bool:
        for c in Signal.clients:
            if c.user.uuid == user_uuid and c.room.room_gid == room_gid:
                return True
        return False

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
        for c in Signal.clients:
            c.add_event(event)

    @staticmethod
    def run():
        log.info("Signal thread started!")
        while True:
            Signal.events_emmitter.wait()
            log.info("Recevied event to emmit")
            while len(Signal.events):
                event: ChatEvent = Signal.get_event()
                if event:
                    log.debug(f"Event: {json.dumps(event.to_json())}")
                    Signal.share_event(event)
            log.debug("Going to sleep...")
            Signal.events_emmitter.clear()
                


def init():
    log.debug("Initing Signal...")
    Signal.events_lock = Lock()
    Signal.events_emmitter = Event()
    Signal.events_emmitter.clear()
    Signal.worker = Thread(target=Signal.run)
    Signal.worker.start()


def emmit(event: ChatEvent):
    Signal.add_event(event)
    Signal.events_emmitter.set()
