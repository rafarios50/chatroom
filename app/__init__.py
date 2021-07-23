from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#Script to create and configurate the app
#Here is defined the database used, in this case a sqlite3 hosted locally 
#in the server in the app.sqlite file

#The testing uses a different database test.sqlite to avoid overwriting the app database

db = SQLAlchemy()

from . import auth, chatroom, dbschema

def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY='\xd7\xde\xcb\x02\x85\xcf\xe9\x96\x8a\x84\xc9\x1a\xf6\xa8\xb0\xe9\xb4\xe0',
        SQLALCHEMY_DATABASE_URI='sqlite:///app.sqlite',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )

    if test_config is not None:
        print("config testing")
        app.config.from_pyfile('config-testing.py', silent=True)
        app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.sqlite'    
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(chatroom.bp)

    app.add_url_rule('/', endpoint='index')

    db.init_app(app)    
    #Creates the tables given by the classes in the db schema
    with app.app_context():
        dbschema.init_db()
  
    return app
