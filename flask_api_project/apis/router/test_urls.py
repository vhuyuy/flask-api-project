from flask_api_project.apis.controller import test_lock
from ...apis.controller import test_mq

urls = [
    '/v1/testlock', test_lock.TestLock,
    '/v1/testrabbitmq', test_mq.TestRabbitMQ,
]
