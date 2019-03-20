class DefaultConfig(dict):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1:3306/cc_dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SUPER_ADMIN = 'admin'

    CORS_ORIGINS = ['*']
    CORS_METHODS = ['POST', 'GET', 'OPTIONS', 'DELETE', 'PATCH', 'PUT']
    CORS_ALLOW_HEADERS = ['Authorization', 'Content-Type']
