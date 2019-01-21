from chalicelib.types import REQUEST, HEADERS, DICT
from typing import List, Tuple
from chalicelib.validator import validate_http
import chalicelib.json_proto as proto
from chalicelib.database.db import Room, Session, Message, User
from datetime import datetime
import re
import string
import secrets
import logging as log
import chalicelib.signal as signal
from chalicelib.chat_event import ChatEvent, EventType

CONFUSING_CHARS = r'[lI10O]'


def create_room(request: REQUEST, headers: HEADERS):
    user = validate_http(headers)
    if not user:
        return proto.error(400, 'Unknown user')
    room = Room()
    room.room_gid = str(generate_room_gid())
    if not room.room_gid:
        return proto.internal_error("Couldn't connect to db")
    room.created = datetime.now()
    room.owner = user.id

    session = Session()
    try:
        session.add(room)
        session.commit()
        return proto.ok(
            {
                'room_gid': room.room_gid
            }
        )
    except Exception as e:
        log.error(e)
        return proto.internal_error('Error while creating room')
    finally:
        session.close()


def send_message(request: REQUEST, headers: HEADERS):
    user = validate_http(headers)
    if not user:
        return proto.error(400, 'Unknown user')
    for p in ['room_gid', 'msg']:
        if not request.get(p):
            return proto.malformed_request(
                'send_message',
                request,
                f'Missing param: {p}')
    room_gid = request.get('room_gid')
    msg = request.get('msg')
    room = get_room_by_room_gid(room_gid)
    if not room:
        return proto.error(404, 'Unknown room')

    message = Message()
    message.room = room.id
    message.sender = user.id
    message.msg = msg
    message.created = datetime.now()

    session = Session()
    try:
        session.add(message)
        session.commit()
        emmitNewMsg(
            session,
            user.uuid,
            room_gid,
            message.id)
        return proto.ok()
    except Exception as e:
        log.error(e)
        return proto.internal_error('Error while adding msg')
    finally:
        session.close()


def room_history(query_params: REQUEST, headers: HEADERS):
    user = validate_http(headers)
    if not user:
        return proto.error(400, 'Unknown user')
    for p in ['room_gid']:
        if not query_params.get(p):
            return proto.malformed_request(
                'send_message',
                query_params,
                f'Missing param: {p}')
    room_gid = query_params.get('room_gid')
    room = get_room_by_room_gid(room_gid)
    if not room:
        return proto.error(404, 'Unknown room')
    msg = load_room_history(room.id)
    log.debug(msg)
    return proto.ok(msg)


def get_room_by_room_gid(room_gid: str) -> Room:
    session = Session()
    try:
        room: Room = session.query(Room).filter_by(
            room_gid=room_gid).one_or_none()
        return room
    except Exception as e:
        log.error(e)
        return None
    finally:
        session.close()


def load_room_history(room_id: int) -> List[DICT]:
    session = Session()
    try:
        messages = session.query(
            User.uuid,
            User.username,
            Message.id,
            Message.msg,
            Message.created).join(
                Message, User.messages).filter(Message.room == room_id).all()
        log.debug(messages)
        return _msg_to_json(messages)
    except Exception as e:
        log.error(e)
        return None
    finally:
        session.close()


def generate_room_gid(length: int = 8) -> str:
    alphanumerics = string.ascii_letters + string.digits
    availables = re.sub(CONFUSING_CHARS, '', alphanumerics)
    session = Session()
    try:
        while True:
            room_gid = ''.join(
                secrets.choice(availables) for i in range(length))
            room: Room = session.query(Room).filter_by(
                room_gid=room_gid).one_or_none()
            if not room:
                return room_gid
    except Exception as e:
        log.error(e)
        return None
    finally:
        session.close()


def _msgs_to_json(messages: List[Tuple]) -> List[DICT]:
    converted = []
    if not messages:
        return converted
    for msg in messages:
        converted.append(_msg_to_json(msg))
    return converted


def _msg_to_json(msg: Tuple) -> DICT:
    if not msg:
        return None
    current = {}
    current['sender'] = {}
    current['sender']['uuid'] = msg[0]
    current['sender']['username'] = msg[1]
    current['msg'] = {}
    current['msg']['msgId'] = msg[2]
    current['msg']['txt'] = msg[3]
    current['msg']['timestamp'] = msg[4].timestamp()
    return current


def emmitNewMsg(session,
                user_uuid: str,
                room_gid: str,
                message_id: int):
    try:
        message = session.query(
            User.uuid,
            User.username,
            Message.id,
            Message.msg,
            Message.created).join(
                Message, User.messages).filter(
                    Message.id == message_id).one_or_none()
        signal.emmit(
            ChatEvent(user_uuid,
                      room_gid,
                      EventType.NEW_MSG,
                      _msg_to_json(message)))
    except Exception as e:
        log.error(e)
