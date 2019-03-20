from ..exceptions.request_error_code import RequestErrorEnum
from ..exceptions.system_error_code import SystemErrorEnum


class RequestException(Exception):

    def __init__(self, enum_code=None, key=None, status_code=200):
        Exception.__init__(self)

        self.status_code = status_code
        if enum_code in RequestErrorEnum:
            self.code = enum_code.get_code()
            if key:
                self.message = '{} - {}'.format(enum_code.get_msg(), key)
            else:
                self.message = enum_code.get_msg()
        else:
            self.code = SystemErrorEnum.INTERNAL_SYSTEM_ERROR.get_code()
            self.message = SystemErrorEnum.INTERNAL_SYSTEM_ERROR.get_msg()
