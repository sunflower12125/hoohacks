import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'testing-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("s://", "sql://", 1)


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ["PROD_SECRET_KEY"]


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True