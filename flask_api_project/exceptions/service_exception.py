from ..exceptions.service_error_code import ServiceErrorEnum
from ..exceptions.system_error_code import SystemErrorEnum


class ServiceException(Exception):

    def __init__(self, enum_code=None, status_code=200):
        Exception.__init__(self)

        self.status_code = status_code
        if enum_code in ServiceErrorEnum:
            self.code = enum_code.get_code()
            self.message = enum_code.get_msg()
        else:
            self.code = SystemErrorEnum.INTERNAL_SYSTEM_ERROR.get_code()
            self.message = SystemErrorEnum.INTERNAL_SYSTEM_ERROR.get_msg()
