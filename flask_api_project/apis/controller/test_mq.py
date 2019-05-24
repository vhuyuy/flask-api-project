from flask_restful import Resource

from ...logger.logger import log
from ...rabbitmq_utils.mq_constants import exchange_t, queue_t
from ...rabbitmq_utils.mq_utils import basic_publish


class TestRabbitMQ(Resource):
    @log.catch(reraise=True)
    def get(self):
        msg = 'hello world'
        basic_publish(exchange_t, queue_t, msg, delivery_mode=2)
        return 1
