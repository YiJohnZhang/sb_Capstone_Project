from flask_sqlalchemy import SQLAlchemy;
from flask_bcrypt import Bcrypt;

db = SQLAlchemy();
bcrypt = Bcrypt();

def connectDatabase(app):
    db.app = app;
    db.init_app(app);

'''Users Model
'''
class User(db.Model):
