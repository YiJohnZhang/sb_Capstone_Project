import os;

from flask import Flask;
from flask_debugtoolbar import DebugToolbarExtension;

from models import db, connectDatabase;
from app import main;

def create_app():

	app = Flask(__name__);
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///sb_capstone_01');
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False; 
	app.config['SQLALCHEMY_ECHO'] = False;
	
	# Configure Sessions (req. for Debug Toolbar)
	app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'afsd');

	# Configure Debug Toolbar
	app.debug = True;
	toolbar = DebugToolbarExtension(app);
	app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False;
	
	db.init_app(app);
	app.register_blueprint(main);

	return app;