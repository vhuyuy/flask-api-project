from datetime import timedelta


class CeleryConfig(dict):

    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_IGNORE_RESULT = True

    CELERYBEAT_SCHEDULE = {
        'task_add': {
            'task': 'flask_api_project.proj.tasks.add',
            'schedule': timedelta(seconds=30),
            'args': (1, 2),
        }
    }
