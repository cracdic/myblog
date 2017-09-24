from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_uploads import UploadSet, configure_uploads, patch_request_class, IMAGES
from markdown import markdown
from config import config
import flask_whooshalchemyplus

bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
db = SQLAlchemy()
pagedown = PageDown()
pictures = UploadSet('pictures', IMAGES)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    pagedown.init_app(app)
    login_manager.init_app(app)
    configure_uploads(app, pictures)
    patch_request_class(app)
    flask_whooshalchemyplus.init_app(app)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
