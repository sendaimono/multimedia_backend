import socket
from threading import Thread
import logging as log
from chalicelib.socket.client import Client
import chalicelib.signal as signal
from chalicelib.chat_event import ChatEvent, EventType
from chalicelib.validator import validate
from chalicelib.room import get_room_by_room_gid
import json


class Server(Thread):
    ip = '127.0.0.1'
    port = 2004
    socket: socket.socket

    def __init__(self):
        Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip, self.port))
        log.debug(f"TCP Server inited on address {self.ip}:{self.port}")

    def run(self):
        while True:
            log.debug("Listening...")
            self.socket.listen()
            (s, c) = self.socket.accept()
            s.setblocking(False)
            # log.debug("Accepted new connection!")
            cli = Client(s, c)
            if self.verify_conn(cli):
                cli.start()
                signal.Signal.add_client(cli)
                # signal.emmit(
                #     ChatEvent(
                #         cli.user.uuid,
                #         cli.room.room_gid,
                #         EventType.JOIN))
            else:
                cli.socket.close()
                log.debug("Invalid connection")

    def verify_conn(self, client: Client) -> bool:
        verify_msg = client.read()
        log.debug(verify_msg)
        try:
            data = json.loads(verify_msg.decode())
        except Exception as e:
            log.error(e)
            return False
        # if signal.Signal.already_connected(
        #     data.get('uuid'), data.get('room_gid')):
        #     return False
        client.user = validate(data.get('uuid'))
        client.room = get_room_by_room_gid(data.get('room_gid'))
        if not client.user or not client.room:
            return False
        return True
