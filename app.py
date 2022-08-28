from flask import Flask;
from flask import request, session, g, render_template, redirect, url_for, flash;
from sqlalchemy.exc import IntegrityError;
    # attempt to re-enter a unique constraint, on result found for admin attempt
from models import db, connectDatabase;
from models import User, Pet;
from models import RoleTable, PetUserJoin, Breed, PetSpecie, CoatDescription, Color;
from forms import LoginForm, RegisterForm, AddEditPetForm, SearchPetForm;
from wtforms.compat import iteritems, itervalues;
from wtforms.validators import InputRequired;

from flask_debugtoolbar import DebugToolbarExtension;
from functools import wraps;
import os;

# Constants
CURRENT_USER_KEY = "currentUser";
RETURN_PAGE_KEY = "previousPage";

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


'''HELPER FUNCTIONS'''
def login(user):
    """Log in user."""

    session[CURRENT_USER_KEY] = user.id;

def logout():
    """Logout user."""

    if CURRENT_USER_KEY in session:
        del session[CURRENT_USER_KEY];

    """Add non-caching headers on every request."""
        
    #   Turn off all caching in Flask: (useful for dev; in production, this kind of stuff is typically handled elsewhere)
    #       https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req

def populatePetFormSelectFields(petForm):
    '''Populates form selection choices to create, edit, and search pet.'''

    # pet_classification = SelectField('Pet Classficiation', validators=[InputRequired()], coerce=int);
    # primary_breed = SelectField('Pet Breed', validators=[InputRequired()], coerce=int);
    #     # null the selection in new pet logic (models.py) if the pet_classificatino is not dog or cat. doesn't need to be that polished.
    #     # manually set it to required if pet_classificatino is dog or cat.

    # coat_hair = SelectField('Coat Hair Type', validators=[InputRequired()], coerce=int);
    # coat_pattern = SelectField('Coat Pattern', validators=[Optional()], coerce=int);

    # primary_light_shade = SelectField('Primary Light Shade', validators=[InputRequired()], coerce=int);
    # primary_dark_shade = SelectField('Primary Dark Shade', validators=[InputRequired()], coerce=int);

    DEFAULT_CHOICE_TUPLE = (0, 'All');

    # Pet Specie
    petSpecieChoices = [DEFAULT_CHOICE_TUPLE];
    databasePetSpecies = PetSpecie.returnAllSpecies();
    for specie in databasePetSpecies:
        petSpecieChoices.append((specie.id, specie.specie_name));
            # Otherwise Jinja yields 'too many values to unpack' error.

    petForm.pet_specie.choices = petSpecieChoices;
        # todo: make it inline
        # todo: change to icons?

    # Pet Breed
    petBreedChoices = [DEFAULT_CHOICE_TUPLE];
    databaseBreedTypes = Breed.returnAllBreeds();
    for databaseBreedType in databaseBreedTypes:
        petBreedChoices.append((databaseBreedType.id, databaseBreedType.breed_name));

    petForm.primary_breed.choices = petBreedChoices;

    
    # Pet Coat, Hair Type
    petHairChoices = [DEFAULT_CHOICE_TUPLE];
    databaseHairTypes = CoatDescription.returnAllHairTypes();
    for databaseHairType in databaseHairTypes:
        petHairChoices.append((databaseHairType.id, databaseHairType.coat_description));

    petForm.coat_hair.choices = petHairChoices;

    # Pet Coat, Coat Type
    petCoatChoices = [DEFAULT_CHOICE_TUPLE]; 
    databaseCoatPatterns = CoatDescription.returnAllCoatTypes();
    for databaseCoatPattern in databaseCoatPatterns:
        petCoatChoices.append((databaseCoatPattern.id, databaseCoatPattern.coat_description));

    petForm.coat_pattern.choices = petCoatChoices;

    # Pet Color, Light
    petLightColorChoices = [DEFAULT_CHOICE_TUPLE];
    databaseLightPetColors = Color.returnAllLightColors();
    for lightPetColor in databaseLightPetColors:
        petLightColorChoices.append((lightPetColor.id, lightPetColor));
        
    petForm.primary_light_shade.choices = petLightColorChoices;

    # Pet Color, Dark
    petDarkColorChoices = [DEFAULT_CHOICE_TUPLE];
    databaseDarkPetColors = Color.returnAllDarkColors();
    for databaseDarkPetColor in databaseDarkPetColors:
        petDarkColorChoices.append((databaseDarkPetColor.id, databaseDarkPetColor));
        # darkPetColors.append([(color.id, color) for color in Color.returnAllDarkColors()]);
            # Jinja yields 'too many values to unpack' error.
    
    petForm.primary_dark_shade.choices = petDarkColorChoices;

    return petForm;

def returnSearchPetForm():
    '''Returns a search Pet form for the index and search views.'''
    
    searchPetForm = SearchPetForm(meta={'csrf': False});
        # disable csrf: https://stackoverflow.com/a/61052386

    # Remove unsearchable fields
    if searchPetForm.pet_name:
        del searchPetForm.pet_name;

    if searchPetForm.description:
        del searchPetForm.description;

    if searchPetForm.image_url:
        del searchPetForm.image_url;

    if searchPetForm.estimated_age:
        del searchPetForm.estimated_age;

    if searchPetForm.age_certainty:
        del searchPetForm.age_certainty;

    if searchPetForm.weight:
        del searchPetForm.weight;

    if searchPetForm.special_needs:
        del searchPetForm.special_needs;

    # petNameValidators = SearchPetForm.description.kwargs.get('validators');
    # print(petNameValidators)
    # print('-----------------------')
        
    for fieldName in iter(searchPetForm._fields):
        # print(fieldName);

        fieldValidators = searchPetForm[fieldName].validators;
        # print(fieldValidators);

        for fieldValidator in fieldValidators:
            # print(fieldValidator);
 
            if isinstance(fieldValidator, InputRequired):
                fieldValidators.remove(fieldValidator);

    # Check Work
    # for fieldName in iter(searchPetForm._fields):
    #     fieldValidators = searchPetForm[fieldName].validators;
    #     for fieldValidator in fieldValidators:
    #         print(fieldValidator);

    # Add choices
    searchPetForm = populatePetFormSelectFields(searchPetForm);

    return searchPetForm;

'''DECORATORS'''
# Before & After Decorators
@app.before_request
def before_request():
    """If we're logged in, add curr user to Flask global."""

    # update current user
    if CURRENT_USER_KEY in session:
        g.user = User.returnUserbyUsername(session[CURRENT_USER_KEY]);

    else:
        g.user = None;

    session[RETURN_PAGE_KEY] = request.referrer;
        # https://stackoverflow.com/a/39777426
        # need the 200 referrer, not the redirect referrrer

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

# Authentication Decorators
def loginRequired_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if not g.user:
            flash("Access unauthorized.", "danger");
            return redirect(url_for('indexView'));
            
        return f(*args, **kwargs);
    
    return wrapper;

def notLoginRequired_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if g.user:
            return redirect(url_for('indexView'));
            
        return f(*args, **kwargs);
    
    return wrapper;

def adminAction_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        return f(*args, **kwargs);
    
    return wrapper;

# Error Decorators
@app.errorhandler(404)
def error_404(error):
    '''404: Not Found View'''
    return render_template('errors/error.html', errorCode = 404, previousPath = session[RETURN_PAGE_KEY]), 404;

@app.errorhandler(403)
def error_403(error):
    '''403: Forbidden View'''
    return render_template('errors/error.html', errorCode = 403, previousPath = session[RETURN_PAGE_KEY]), 403;

# Helper Decorators




# Routes
@app.route('/')
def indexView():

    searchPetForm = returnSearchPetForm();

    statistics = {
        'users': User.returnNumberOfUsers(),
        'rescueOrganizations': RoleTable.returnNumberOfRescueOrganizations(),
        'pets': Pet.returnNumberOfPets(), 
    };

    return render_template('index.html',
        form = searchPetForm, displayFormLabel = True, 
        statistics=statistics);

