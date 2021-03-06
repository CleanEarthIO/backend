import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, static_folder="web/build/static", template_folder="web/build")
    app.secret_key = os.environ.get('SECRET')
    project_dir = os.path.dirname(os.path.abspath(__file__))
    database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))
    app.config['SQLALCHEMY_DATABASE_URI'] = database_file
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    return app
