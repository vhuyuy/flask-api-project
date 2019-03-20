import os

from flask import Flask

from .apis import urls
from .config.celery_config import CeleryConfig
from .config.default_config import DefaultConfig
from .extensions import cors, db, swagger, celery
from .logger.logger import log, init

_default_instance_path = '%(instance_path)s/instance' % \
                         {'instance_path': os.path.dirname(os.path.realpath(__file__))}


def create_app():
    app = Flask(__name__, instance_relative_config=True, instance_path=_default_instance_path)
    configure_app(app)
    configure_logging()
    # configure_error(app)
    configure_celery(app, celery)
    configure_extensions(app)
    configure_blueprint(app)
    log.info('server start...')
    return app


# def configure_app(app):
#     if os.environ.get('STAGING_CONFIG'):
#         app.config.from_envvar('STAGING_CONFIG')
#         return
#
#     if os.environ.get('PRODUCTION_CONFIG'):
#         app.config.from_envvar('PRODUCTION_CONFIG')
#         return
#
#     if os.environ.get('DEV_CONFIG'):
#         app.config.from_envvar('DEV_CONFIG')
#         return
def configure_app(app):
    app.config.from_object(CeleryConfig)
    app.config.from_object(DefaultConfig)
    app.config.from_pyfile('dev.py')


def configure_logging():
    init()


def configure_celery(app, celery):
    app.config.update({"BROKER_URL": app.config["CELERY_BROKER_URL"]})
    celery.conf.update(app.config)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask


def configure_extensions(app):
    # cors
    cors.init_app(app,
                  origins=app.config['CORS_ORIGINS'],
                  methods=app.config['CORS_METHODS'],
                  allow_headers=app.config['CORS_ALLOW_HEADERS'])
    # db
    db.init_app(app)

    # swagger
    swagger.init_app(app)


def configure_blueprint(app):
    urls.register_blueprint(app)
