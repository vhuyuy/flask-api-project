from pika import BasicProperties
from pika.exceptions import ConnectionClosed

from ..logger.logger import log
from ..rabbitmq_utils.mq_extensions import fpika


# This is producer
# params: properties = BasicProperties(delivery_mode=2)
#           delivery_mode=2 means that message is durable
def basic_publish(exchange, bind_key, msg, delivery_mode=None):
    properties = None
    channel = fpika.channel()
    channel.confirm_delivery()

    try:
        if delivery_mode is not None:
            properties = BasicProperties(delivery_mode=delivery_mode)

        result = channel.basic_publish(exchange, bind_key, msg, properties=properties)
        log.info(result)
        # if not result:
        #     While result is False, need requeue and consumer the message
        fpika.return_channel(channel)
    except ConnectionClosed as e:
        log.error('Error. Connection closed, and the message was never delivered.')
