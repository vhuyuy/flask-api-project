# sqlalchemy
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@ip:port/database'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

# cors
CORS_ORIGINS = ['*']
CORS_METHODS = ['POST', 'GET', 'OPTIONS', 'DELETE', 'PATCH', 'PUT']
CORS_ALLOW_HEADERS = ['Authorization', 'Content-Type']

REDIS_HOST = 'localhost'
REDIS_PASSWORD = '123456'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_CLASS = 'redis.StrictRedis'
