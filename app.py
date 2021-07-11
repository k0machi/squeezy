from functools import reduce
from flask import Flask, render_template
from flask_security import Security, SQLAlchemyUserDatastore
from database import db
from squeezy.controllers.main import main_module
from squeezy.controllers.api import api_module
from squeezy.models.settings import Settings
from squeezy.models.user import User
from squeezy.models.role import Role
from config import ENVIRONMENT

def init_app():
    app = Flask("Squeezy")
    app.config["SQLALCHEMY_DATABASE_URI"] = ENVIRONMENT.get("DATABASE_URL")
    app.config["SECRET_KEY"] = ENVIRONMENT.get("SECRET_KEY")
    app.config["SECURITY_PASSWORD_SALT"] = ENVIRONMENT.get("SECURITY_PASSWORD_SALT")
    init_blueprints(app)
    init_extensions(app)
    return app


def setup_db(app: Flask):
    with app.app_context():
        db.create_all()
    

def init_blueprints(app: Flask):
    app.register_blueprint(main_module)
    app.register_blueprint(api_module)


def init_extensions(app: Flask):
    db.init_app(app)


def create_default_user():
    if len(User.query.all()) == 0:
        DATASTORE.create_user(email="admin@localhost", password="admin")
        db.session.commit()


def init_proxy_settings():
    if len(Settings.query.all()) == 0:
        proxy_settings = [(setting[0].lstrip("SQUID_").lower(), setting[1]) for setting in ENVIRONMENT.items() if setting[0].startswith("SQUID_")]
        for key, value in proxy_settings:
            s = Settings(key=key, value=value)
            db.session.add(s)
        db.session.commit()
            
            


app = init_app()
setup_db(app)
DATASTORE = SQLAlchemyUserDatastore(db, User, Role)
SECURITY = Security(app, DATASTORE)
app.before_first_request(create_default_user)
app.before_first_request(init_proxy_settings)

if __name__ == "__main__":
   app.run(host="0.0.0.0")