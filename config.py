__author__ = 'nitin'

import os

basedir = os.path.abspath(os.path.dirname(__file__))
database_name = 'demeter'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://sqladmin:Qwedsazxc123@staging-mysql.c0wj8qdslqom.ap-southeast-1.rds.amazonaws.com/' + database_name

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://sqladmin:Qwedsazxc123@staging-mysql.c0wj8qdslqom.ap-southeast-1.rds.amazonaws.com/' + database_name

class ProductionConfig(Config):
    PRODUCTION = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://sqladmin:Qwedsazxc123@staging-mysql.c0wj8qdslqom.ap-southeast-1.rds.amazonaws.com/' + database_name

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
