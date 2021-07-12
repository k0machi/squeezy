import logging
from flask import Flask, g
from flask_security import Security, SQLAlchemyUserDatastore
from database import db
from squeezy.controllers.main import main_module
from squeezy.controllers.api import api_module
from squeezy.models.settings import Settings
from squeezy.models.user import User
from squeezy.models.role import Role
from config import ENVIRONMENT
from logging.config import dictConfig

def init_app():
    init_logging()
    app = Flask("Squeezy")
    app.config["SQLALCHEMY_DATABASE_URI"] = ENVIRONMENT.get("DATABASE_URL")
    app.config["SECRET_KEY"] = ENVIRONMENT.get("SECRET_KEY")
    app.config["SECURITY_PASSWORD_SALT"] = ENVIRONMENT.get("SECURITY_PASSWORD_SALT")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    init_blueprints(app)
    init_extensions(app)
    return app


def init_logging():
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/application.log',
                'formatter': 'default',
                'maxBytes': 10480240,
                'backupCount': 4
            }
        },
        'root': {
            'level': ENVIRONMENT.get("LOG_LEVEL"),
            'handlers': ['wsgi', 'file']
        }
    })


def setup_db(app: Flask):
    logging.info("setup_db: Checking database schema")
    with app.app_context():
        db.create_all()
    

def init_blueprints(app: Flask):
    logging.info("init_blueprints: Initializing blueprints")
    app.register_blueprint(main_module)
    app.register_blueprint(api_module)


def init_extensions(app: Flask):
    db.init_app(app)


def create_default_user():
    if len(User.query.all()) == 0:
        DATASTORE.create_user(email="admin@localhost", password="admin")
        db.session.commit()
        logging.info("Initial user created! Credentials: admin@localhost/admin ")


def init_proxy_settings():
    if len(Settings.query.all()) == 0:
        proxy_settings = [(setting[0].lstrip("SQUID_").lower(), setting[1]) for setting in ENVIRONMENT.items() if setting[0].startswith("SQUID_")]
        for key, value in proxy_settings:
            s = Settings(key=key, value=value)
            db.session.add(s)
        db.session.commit()
            
          
app = init_app()
app.before_first_request(create_default_user)
app.before_first_request(init_proxy_settings)
setup_db(app)
DATASTORE = SQLAlchemyUserDatastore(db, User, Role)
SECURITY = Security(app, DATASTORE)

if __name__ == "__main__":
   app.run(host="0.0.0.0")