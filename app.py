import logging as log
import os
import json

from chalice import Chalice
import chalicelib.json_proto as proto
import chalicelib.users as users
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

def get_abs_path():
    abs_path = os.path.dirname(os.path.realpath(__file__))
    chalicelib.common.ENV_VARIABLES.ABS_PATH = abs_path

init_log(log)
get_abs_path()



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