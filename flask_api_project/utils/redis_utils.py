from flask_api_project.extensions import redis_store


def get(key):
    x = redis_store.get(key).decode('utf-8')
    return x
