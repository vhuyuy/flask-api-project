from ..logger.logger import log
from ..rabbitmq_utils.flask_pika import Pika
from ..rabbitmq_utils.mq_constants import exchange_t, queue_t, fanout

fpika = Pika()


def mq_bind(exchange, queue, exchange_type, durable=False):
    channel = fpika.channel()
    channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=True)
    channel.queue_declare(queue=queue, durable=durable)
    channel.queue_bind(exchange=exchange, queue=queue)


def bind_init():
    mq_bind(exchange_t, queue_t, fanout, True)
    log.info('RabbitMQ has been ready.')
