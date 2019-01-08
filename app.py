import logging as log
import os
import json

from chalice import Chalice
import chalicelib.json_proto as proto
import chalicelib.users as users
import chalicelib.room as room
import chalicelib.common

app = Chalice(app_name='chat')
app.debug = True


def init_log(log):
    log_level = os.getenv('DEFAULT_LOG_LEVEL') or 'DEBUG'
    level = getattr(log, log_level) if hasattr(log, log_level) else log.WARNING
    print(f"log level: {log_level}")
    log.basicConfig(
        level=level,
        format='%(asctime)s %(levelname)-8s [%(name)s.%(funcName)s:%('
               'lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logger = log.getLogger()
    logger.setLevel(level=log_level)


init_log(log)


@app.route(
    '/login',
    methods=['POST'],
    content_types=[
        'text/plain',
        'application/json'
    ]
)
def login():
    return _forward_json_to(users.login_user)


@app.route(
    '/register',
    methods=['POST'],
    content_types=[
        'text/plain',
        'application/json'
    ]
)
def register():
    return _forward_json_to(users.register_user)


@app.route(
    '/create-room',
    methods=['POST'],
    content_types=[
        'text/plain',
        'application/json'
    ]
)
def create_room():
    return _forward_json_and_headers_to(room.create_room)


@app.route(
    '/send-message',
    methods=['POST'],
    content_types=[
        'text/plain',
        'application/json'
    ]
)
def send_message():
    return _forward_json_and_headers_to(room.send_message)


@app.route(
    '/get-room-history',
    methods=['GET']
)
def get_room_history():
    return _forward_query_params_and_headers_to(room.room_history)


def _forward_json_to(fun):
    try:
        raw_body = app.current_request.raw_body
        log.info(f"raw_body of request: {raw_body}")
        params = json.loads(raw_body.decode())
    except json.decoder.JSONDecodeError:
        log.error('Invalid data')
        return proto.error(400, 'Invalid data.')
    else:
        return fun(params)


def _forward_json_and_headers_to(fun):
    try:
        raw_body = app.current_request.raw_body
        log.info(f"raw_body of request: {raw_body}")
        params = json.loads(raw_body.decode())
        headers_as_json = (
            dict((k.lower(), v)
                 for k, v in app.current_request.headers.items()))
        log.info(f'headers: {headers_as_json}')
    except json.decoder.JSONDecodeError:
        log.error('Invalid data')
        return proto.error(400, 'Invalid data.')
    else:
        return fun(params, headers_as_json)


def _forward_query_params_and_headers_to(fun):
    query_params = app.current_request.query_params
    log.info(f"query_params of request: {query_params}")
    headers_as_json = (
        dict((k.lower(), v)
             for k, v in app.current_request.headers.items()))
    log.info(f'headers: {headers_as_json}')
    return fun(query_params, headers_as_json)
