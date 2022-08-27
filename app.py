from flask import Flask;
from flask import request, render_template, redirect, url_for, flash;
from sqlalchemy.exc import IntegrityError;
    # attempt to re-enter a unique constraint, on result found for admin attempt
from models import db, connectDatabase;
from forms import LoginForm, RegisterForm, AddEditPetForm;

from flask_debugtoolbar import DebugToolbarExtension;
import os;

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

connectDatabase(app);
db.create_all();

@app.after_request
def after_request(req):
    """Add non-caching headers on every request."""
        
    #   Turn off all caching in Flask: (useful for dev; in production, this kind of stuff is typically handled elsewhere)
    #       https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req

# Routes
@app.route('/')
def indexView():
    return render_template('index.html');

