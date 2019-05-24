import os

import sqlalchemy
from flask import make_response
from flask_restful import Api as BaseApi
from kafka.producer import kafka
from sqlalchemy.exc import DBAPIError
from werkzeug.exceptions import HTTPException

from ..exceptions.request_exception import RequestException
from ..exceptions.service_exception import ServiceException
from ..exceptions.system_error_code import SystemErrorEnum
from ..exceptions.system_exception import SystemException
from ..utils.response_utils import error


class Api(BaseApi):

    def __init__(self, app=None, prefix='',
                 default_mediatype='application/json', decorators=None,
                 catch_all_404s=True, serve_challenge_on_401=False,
                 url_part_order='bae', errors=None):
        super().__init__(app, prefix,
                         default_mediatype, decorators,
                         catch_all_404s, serve_challenge_on_401,
                         url_part_order, errors)

    def handle_error(self, e):

        # got_request_exception.send(current_app._get_current_object(), exception=e)

        status_code = 200

        if isinstance(e, HTTPException):
            code = e.code
            return make_response(e.get_body(), code)
        elif isinstance(e, sqlalchemy.exc.DatabaseError):
            e = SystemErrorEnum.DATABASE_ERROR
            result = error(msg=e.get_msg(), error_code=e.get_code())
        elif isinstance(e, kafka.Errors.KafkaError):
            e = SystemErrorEnum.KAFKA_ERROR
            result = error(msg=e.get_msg(), error_code=e.get_code())
        elif isinstance(e, RequestException) \
                or isinstance(e, ServiceException) \
                or isinstance(e, SystemException):
            result = error(msg=e.message, error_code=e.code, http_status_code=e.status_code)
        else:
            # todo record or mail

            result = error(
                msg=str(e) if not os.environ.get('PRODUCTION_CONFIG') else 'System busy',
                error_code=99,
                http_status_code=status_code
            )

        return result
