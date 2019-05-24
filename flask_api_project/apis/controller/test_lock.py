import random

from flask_restful import Resource

from ...exceptions.service_error_code import ServiceErrorEnum
from ...extensions import redis_store
from ...logger.logger import log
from ...utils import redis_utils
from ...utils.response_utils import ok, error


class TestLock(Resource):
    @log.catch(reraise=True)
    def get(self):
        x = int(redis_utils.get('good_nums'))

        if x <= 0:
            code = ServiceErrorEnum.SOURCE_HAS_SOLD_OUT

            return error(error_code=code)

        lock = redis_store.lock('goods', timeout=10)
        if lock.acquire(blocking_timeout=0.1):

            x = int(redis_store.get('good_nums'))
            if x > 0:
                r = (random.randint(1, 3))
                if x < r:
                    r = x
                x = redis_store.decr('good_nums', r)
                lock.release()
                return ok(data=x)
            else:
                lock.release()
                code = ServiceErrorEnum.SOURCE_HAS_SOLD_OUT
                return error(error_code=code)
        else:
            code = ServiceErrorEnum.NOT_GRABBED
            return error(error_code=code)
