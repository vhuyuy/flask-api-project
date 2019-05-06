import redis
from celery import Celery
from flasgger import Swagger
from flask_cors import CORS
from flask_redis import Redis
from flask_sqlalchemy import SQLAlchemy

'''
init tools
'''
# redis_store = StrictRedis(port=16379)

# redis_store = Redis(port=16379, decode_responses=True)
redis_store = Redis()

celery = Celery('flask_api_project', include=['flask_api_project.proj.tasks'])

cors = CORS()

db = SQLAlchemy()

template = {
    'swagger': '2.0',
    'info': {
        'title': 'API文档',
        'version': '0.0.1',
    },
    'securityDefinitions': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Bearer <jwt>',
        },
    },
}
swagger = Swagger(template=template)
