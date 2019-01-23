import logging as log
import os
import json

import chalicelib.json_proto as proto
import chalicelib.users as users
import chalicelib.room as room
import chalicelib.common
import chalicelib.signal as signal
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, disconnect, emit
from flask_cors import CORS
from chalicelib.socket.client import Client

app = Flask(__name__)
CORS(app)
io = SocketIO(app, ping_interval=1, ping_timeout=2)


def init_log(log):
    log.getLogger('werkzeug').setLevel(log.ERROR)
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


@io.on('disconnect')
def on_disconnect():
    signal.Signal.remove_client(request.sid)


@io.on('auth')
def on_auth(msg):
    log.info('auth request')
    log.info(msg)
    log.debug(f'Clients: {len(signal.Signal.clients)}')
    cli = Client(request.sid)
    if not (cli.verify(msg) and
            not signal.Signal.already_connected(cli)):
        log.info('invalid request')
        disconnect()
    else:
        log.info('Connected!')
        signal.Signal.add_client(cli)
        log.debug(f'Clients after: {len(signal.Signal.clients)}')
    # emit('test', {'kk': 'asdf'}, room=sids[-2])


@app.route(
    '/login',
    methods=['POST'],
)
def login():
    return _forward_json_to(users.login_user)


@app.route(
    '/register',
    methods=['POST'],
)
def register():
    return _forward_json_to(users.register_user)


@app.route(
    '/create-room',
    methods=['POST'],
)
def create_room():
    return _forward_json_and_headers_to(room.create_room)


@app.route(
    '/send-message',
    methods=['POST'],
)
def send_message():
    return _forward_json_and_headers_to(room.send_message)


@app.route(
    '/get-room-history',
    methods=['GET'],
)
def get_room_history():
    return _forward_query_params_and_headers_to(room.room_history)


def _forward_json_to(fun):
    try:
        raw_body = request.get_data()
        log.info(f"raw_body of request: {raw_body}")
        params = json.loads(raw_body.decode())
    except json.decoder.JSONDecodeError:
        log.error('Invalid data')
        return jsonify(proto.error(400, 'Invalid data.'))
    else:
        return jsonify(fun(params))


def _forward_json_and_headers_to(fun):
    try:

        raw_body = request.get_data()
        log.info(f"raw_body of request: {raw_body}")
        params = json.loads(raw_body.decode())
        headers_as_json = (
            dict((k.lower(), v)
                 for k, v in request.headers.items()))
        log.info(f'headers: {headers_as_json}')
    except json.decoder.JSONDecodeError:
        log.error('Invalid data')
        return jsonify(proto.error(400, 'Invalid data'))
    else:
        return jsonify(fun(params, headers_as_json))


def _forward_query_params_and_headers_to(fun):
    query_params = request.args
    log.info(f"query_params of request: {query_params}")
    headers_as_json = (
        dict((k.lower(), v)
             for k, v in request.headers.items()))
    log.info(f'headers: {headers_as_json}')
    return jsonify(fun(query_params, headers_as_json))


if __name__ == '__main__':
    signal.init(io)
    app.debug = True
    io.run(app, '127.0.0.1', 8000)
