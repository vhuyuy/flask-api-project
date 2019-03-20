from enum import unique

from ..exceptions.enum_core import BaseEnum


# request error level(201xxx)
@unique
class RequestErrorEnum(BaseEnum):
    PARAMETER_ERROR = {"201001": "Param error [required/type/etc.]?"}
    JSON_PARSE_FAIL = {"201002": "JSON parse error"}
