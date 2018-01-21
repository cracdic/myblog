# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config: 
    BLOG_ADMIN = os.environ.get('BLOG_ADMIN')    
    FLASKY_DB_QUERY_TIMEOUT = 0.5
    FLASKY_MAIL_SUBJECT_PREFIX = '[SlugBlog]'
    FLASKY_MAIL_SENDER = 'Slug Admin <Slug@Striped.com>'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') 
    POSTS_PER_PAGE = 7
    SQLALCHEMY_RECORD_QUERIES = True
    SSL_DISABLE = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or "string haven't been set"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    UPLOADED_PICTURES_DEST = '/usr/pictures/uploads'
    RENDER_PICTURES_DEST = '/_uploads/pictures/'
    WHOOSE_BASE = '/tmp/whoosh'
   

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        ('mysql+pymysql://' + os.environ.get('MYSQL_USERNAME') + ':' + 
         os.environ.get('MYSQL_PASSWORD') + '@localhost:3306/blogDevDB')
 
class TestingConfig(Config):
    WTF_CSRF_ENABLED = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        ('mysql+pymysql://' + os.environ.get('MYSQL_USERNAME') + ':' + 
         os.environ.get('MYSQL_PASSWORD') + '@localhost:3306/blogTestDB')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        ('mysql+pymysql://' + os.environ.get('MYSQL_USERNAME') + ':' + 
         os.environ.get('MYSQL_PASSWORD') + '@localhost:3306/blogDB')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # handle the head of internal proxy
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)
        # send error email
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if gettattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
                fromaddr=cls.FLASKY_MAIL_SENDER,
                toaddrs=[cls.BLOG_ADMIN],
                subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + 'Application Error',
                credentials=credentials,
                secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': ProductionConfig
}
