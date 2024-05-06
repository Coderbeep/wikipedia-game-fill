from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from jinja2.filters import FILTERS

db = SQLAlchemy()

def mdebug(env, value):
    print(len(value), flush=True)
    return value

FILTERS['mdebug'] = mdebug

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    db.init_app(app) 

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
