# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or "string haven't been set"
    BLOG_ADMIN = os.environ.get('BLOG_ADMIN')
    UPLOADED_PICTURES_DEST = '/pictures/uploads'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WHOOSE_BASE = '/tmp/whoosh'
    POSTS_PER_PAGE = 15

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
            'mysql+pymysql://myblog:myblog@!@#$@localhost:3306/blogDevDB'
 
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'mysql+pymysql://myblog:myblog@!@#$@localhost:3306/blogTestDB'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://myblog:myblog@!@#$@localhost:3306/blogDB'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
