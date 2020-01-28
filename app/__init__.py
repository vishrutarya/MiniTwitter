# python packages
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from elasticsearch import Elasticsearch
# flask extensions
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
# local modules
from config import Config


# instantiate extensions without attaching to the app
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()

# configure LoginManager object which view function handles logins
login.login_view = 'auth.login' 
login.login_message = 'Please log in to access this page.'

# application factory: create and return configured app instance
def app_factory(config_class=Config):
    # create and configure app instance
    app = Flask(__name__)
    app.config.from_object(Config)

    # attach extensions to app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    # create elasticsearch instance
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None
    # note: can't create the elasticsearch instance in the global scope
    # as with the other extensions b/c it's not wrapped by a Flask extension.
    # It needs to be initialized through the app's config file (app.config),
    # and, therefore, can only be instantiated after the app itself has been
    # instantiated. therefore, elasticsearch is instantiated as an attribute 
    # within the app_factory function on the app object
    # note: if no elasticsearch URL is returned, this will signal that 
    # elasticsearch should be disabled.

    # register blueprints
    from app.errors import bp as errors_bp
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    app.register_blueprint(errors_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth') 
    app.register_blueprint(main_bp)

    # Error logging
    if not app.debug and not app.testing:
        # setup logging to email
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'],
                subject='MiniTwitter Failure',
                credentials=auth,
                secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        # setup logging to local files
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            'logs/minitwitter.log',
            maxBytes=10240,
            backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('MiniTwitter startup')

    return app


from app import models