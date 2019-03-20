from datetime import datetime
from enum import Enum

import requests
from flask import g, request, current_app
from flask_restful import reqparse
from werkzeug import datastructures

from ..exceptions.request_error_code import RequestErrorEnum
from ..exceptions.request_exception import RequestException
from ..exceptions.system_error_code import SystemErrorEnum
from ..exceptions.system_exception import SystemException
from ..logger.logger import log


def obj_to_dict(obj, keys=None, *, display=True, format_time='%Y-%m-%d %H:%M:%S'):
    '''Get the specified key value of the model
    :param obj: The model object to be converted.
    :param keys: Key name to process. What you want to include or not in the returned results, e.g. ['name', 'sex']
    :param display: If it is "True", the :keys: includes the result of the return, otherwise it is excluded.
    :param format_time: Format a field that is a datetime type
    '''
    dict_result = {}
    obj_values = obj.__dict__

    for key in obj_values:
        if key == '_sa_instance_state':
            continue
        key_value = obj_values.get(key)
        if display and key in keys \
                or not display and key not in keys:
            if isinstance(key_value, datetime):
                dict_result[key] = datetime.strftime(key_value, format_time)
            elif isinstance(key_value, Enum):
                dict_result[key] = key_value.value
            else:
                dict_result[key] = key_value
    return dict_result


# use in result which no date or enum
# otherwise use line 14 obj_to_dict() please
def get_dict(result, *args):
    return dict(zip(*args, result))


def _get_request():
    if 'req' not in g:
        g.req = reqparse.RequestParser()
    return g.req


def get_argument(key, *, default=None, type=str, location=None, required=False):
    kwargs = dict(default=default, type=type)
    if location:
        kwargs['location'] = location
    if type == 'file':
        kwargs['type'] = datastructures.FileStorage
        kwargs['location'] = location if location else 'files'

    parser = _get_request()
    parser.add_argument(key, **kwargs)
    try:
        args = parser.parse_args()
    except Exception as e:
        log.error('Param error [required/type/etc.]? - {}', key)
        raise RequestException(RequestErrorEnum.PARAMETER_ERROR, key)

    if required and (args[key] is None or type == str and args[key].strip() == ''):
        log.error('Param error [required/type/etc.]? - {}', key)
        raise RequestException(RequestErrorEnum.PARAMETER_ERROR, key)

    return args[key]


def get_request_ip():
    if request.remote_addr == '127.0.0.1':
        return '127.0.0.1'
    ip_list = request.headers['X-Forwarded-For']
    ip = ip_list.split(',')[0]
    return ip


def rpc_client(method, params):
    url = current_app.config['RPC_URL']
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
    }
    headers = {'Content-type': 'application/json'}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=1)

        if response.status_code == 200:
            reply = response.json()
            log.debug(reply)
            if 'result' in reply:
                return True, reply['result']
            else:
                err = reply['error']
                err['code'] = SystemErrorEnum.REMOTE_SERVICE_ERROR.get_code()
                return False, err
    except Exception as e:
        if isinstance(e, TimeoutError):
            raise SystemException(SystemErrorEnum.READ_TIMED_OUT_ERROR)

        # todo record or mail to admin to solve the exception
        raise SystemException(SystemErrorEnum.REMOTE_SERVICE_ERROR)
