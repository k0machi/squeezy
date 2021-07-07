from flask import Flask, render_template
from flask_security import Security, SQLAlchemyUserDatastore
from dotenv import dotenv_values
from database import db
from squeezy.controllers.main import main_module
from squeezy.models.user import User
from squeezy.models.role import Role
import os


ENVIRONMENT = {
    **dotenv_values(".env.shared"),
    **dotenv_values(".env.local"),
    **os.environ,
}


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


def init_extensions(app: Flask):
    db.init_app(app)


def create_default_user():
    if len(User.query.all()) == 0:
        datastore.create_user(email="admin@localhost", password="admin")
        db.session.commit()


app = init_app()
setup_db(app)
datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, datastore)
app.before_first_request(create_default_user)

if __name__ == "__main__":
    app.run()