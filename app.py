from flask import Flask;
from flask import request, session, g, jsonify, render_template, redirect, url_for, flash, abort;
from sqlalchemy.exc import IntegrityError, InvalidRequestError;
    # attempt to re-enter a unique constraint, on result found for admin attempt
from models import db, connectDatabase;
from models import User, Pet;
from models import RoleTable, PetUserJoin, Breed, PetSpecie, CoatDescription, Color;
from forms import LoginForm, RegisterForm, RequestElevatedForm, EditUserForm, AddEditPetForm, SearchPetForm;
    # add favoritepet?
from wtforms.compat import iteritems, itervalues;
from wtforms.validators import InputRequired;

from flask_debugtoolbar import DebugToolbarExtension;
from functools import wraps;
import os;

import random;
import string;

# Constants
CURRENT_USER_KEY = "currentUser";
RETURN_PAGE_KEY = "previousPage";
IS_USER_ELEVATED_KEY = "isElevated";
USER_ROLE_KEY = "userRole";
    # all users get this figure toggled to obfuscate the session key. good thing the session key mutates after every session (login/logout)
    # also, this to reduce db queries?
OBFUSCATION_STRING_KEY = 'obfuscationString';
OBFUSCATION_STRING_LENGTH = 9;
    # gibberish to change the session key every request

# Search Constants
DEFAULT_CHOICE_TUPLE = (0, 'All');

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
def login(userObject):
    """Log in user."""

    session[CURRENT_USER_KEY] = userObject.username;
    session[IS_USER_ELEVATED_KEY] = userObject.is_elevated;

    elevatedUser = RoleTable.returnRoleIDByUsername(userObject.username);
    if elevatedUser:
        session[USER_ROLE_KEY] = elevatedUser.role_id;
    else:
        session[USER_ROLE_KEY] = None;

def logout():
    """Logout user."""

    if CURRENT_USER_KEY in session:
        session.clear();

# ????
def authenticate(username):
    '''Authenticate that the user in session is the same.'''

    if g.user == User.returnUserbyUsername(username):
        return True;

    return abort(403);

def returnSiteStatistics():

    statistics = {
        'users': User.returnNumberOfUsers(),
        'rescueOrganizations': RoleTable.returnNumberOfRescueOrganizations(),
        'pets': Pet.returnNumberOfPets(), 
    };

    return statistics;


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
    # databaseBreedTypes = Breed.returnAllBreeds();
    # for databaseBreedType in databaseBreedTypes:
    #     petBreedChoices.append((databaseBreedType.id, databaseBreedType.breed_name));

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

def generateObfuscationString(stringLength):
    '''Obfuscates the session key if intercepted and generates a new one every time.'''

    obfuscatedString = ''.join(random.choice(string.printable) for index in range(stringLength));
    return obfuscatedString;

'''DECORATORS'''
# Before & After Decorators
@app.before_request
def before_request():
    """If we're logged in, add curr user to Flask global."""

    session[OBFUSCATION_STRING_KEY] = generateObfuscationString(OBFUSCATION_STRING_LENGTH);
        # obfuscation test. yes it will store extra data and obfuscate the original key because session is a dict itself.
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

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate";
    req.headers["Pragma"] = "no-cache";
    req.headers["Expires"] = "0";
    req.headers['Cache-Control'] = 'public, max-age=0';
    return req;

# Authentication Decorators
def loginRequired_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if not g.user:
            flash("Access unauthorized.", "danger");
            return redirect(url_for('indexView'));
            
        return f(*args, **kwargs);
    
    return wrapper;

def logoutRequired_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        
        if g.user:
            return redirect(url_for('indexView'));
            
        return f(*args, **kwargs);
    
    return wrapper;

# ?????
def privateAuthentication_decorator(f):
    # troll idea: see if i can put a decorator before this one :P
    @wraps(f)
    def wrapper(*args, **kwargs):

        # authenticate helpermethod
        return f(*args, **kwargs);
    
    return wrapper;


def elevatedAction_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        # authenticate helpermethod
        return f(*args, **kwargs);
    
    return wrapper;

def rescueOrganizationAction_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # authenticate helpermethod
        return f(*args, **kwargs);
    
    return wrapper;

def adminAction_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # authenticate helpermethod

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

'''ROUTES'''
''' Public Routes
'''
# General Public Routes
@app.route('/')
def indexView():

    searchPetForm = returnSearchPetForm();

    return render_template('index.html',
        form = searchPetForm, displayFormLabel = True, 
        statistics=returnSiteStatistics());

@app.route('/search')
def searchView():
    # todo. basically the above, but with more information and querying.
        # return render_template();
    return;

@app.route('/pet/<int:petID>')
def petView(petID):

    petObject = Pet.returnPetByID(petID);

    return petObject.pet_name;

# General Public Exclusive Routes
@app.route('/login', methods=['GET', 'POST'])
@logoutRequired_decorator
def loginView():

    loginForm = LoginForm();

    if loginForm.validate_on_submit():
        

        if not User.gracefullyReturnUserByUsername(request.form.get('username')):

            #don't give more information
            loginForm.encrypted_password.errors = ['Incorrect username/password combination.'];
            return render_template('onboarding.html',
                form=loginForm, onboardingAction='login',
                statistics=returnSiteStatistics());

        userObject = User.authentication(request.form.get('username'), request.form.get('encrypted_password'));

        if userObject:

            login(userObject);
            return redirect(url_for('indexView'));
        
        else:
            
            loginForm.encrypted_password.errors = ['Incorrect username/password combination.'];
            return render_template('onboarding.html',
                form=loginForm, onboardingAction='login',
                statistics=returnSiteStatistics());
        
    return render_template('onboarding.html',
        form=loginForm, onboardingAction='login',
        statistics=returnSiteStatistics());

@app.route('/signup', methods=['GET', 'POST'])
@logoutRequired_decorator
def registerView():

    registerForm = RegisterForm();

    if registerForm.validate_on_submit():

        try:

            userObject = User.createUser(request.form);
            db.session.commit();
                
            ''' except InvalidRequestError:

                # SQLAlchemy raises `InvalidRequestError` instead of `IntegrityError`,  if no commit, for violating UNIQUE constraint
                
                registerForm.username.errors = ['Username already taken.'];
                
                # a redirect will smother the error
                return render_template('onboarding.html',
                    form=registerForm, onboardingAction='signup',
                    statistics=returnSiteStatistics());'''

        except IntegrityError:

            db.session.rollback();
                # This version of SQLAlchemy raises `InvalidRequestError` instead of `IntegrityError`, if no rollback is issued, for violating UNIQUE constraint
                    # https://stackoverflow.com/a/67566890
            registerForm.username.errors = ['Username already taken.'];
            
            # a redirect will smother the error, therefore use render_template
            return render_template('onboarding.html',
                form=registerForm, onboardingAction='signup',
                statistics=returnSiteStatistics());
        
        login(userObject);
        return redirect(url_for('indexView'));

    return render_template('onboarding.html',
        form=registerForm, onboardingAction='signup',
        statistics=returnSiteStatistics());

@app.route('/rescueSignup', methods=['GET', 'POST'])
@logoutRequired_decorator
def organizationRegisterView():

    organizationRequestForm = RequestElevatedForm();

    if organizationRequestForm.validate_on_submit():
        # beyond scope of the project
        organizationRequestForm.message.errors = ['Sorry! This feature is still in Work-in-Progress.'];
        return render_template('onboarding.html',
            form=organizationRequestForm, onboardingAction='request',
        statistics=returnSiteStatistics());

    return render_template('onboarding.html',
        form=organizationRequestForm, onboardingAction='request',
        statistics=returnSiteStatistics());

''' Private Routes
'''
# General Private Routes
@app.route('/logout')
@loginRequired_decorator
def logoutView():
    logout();
    return redirect(url_for('indexView'));

# User Routes
@app.route('/user/<username>')
def userView(username):
    # todo.
    # return user information and display it.

    userObject = User.returnUserbyUsername(username);

    return userObject.username;

@app.route('/user/<username>/edit', methods=['GET', 'POST'])
@loginRequired_decorator
def editUserView(username):
    # todo.
    userObject = User.returnUserbyUsername(username);
    # have a form for editing the user. authenticate the action
    # editUserForm = EditUserForm();
    
    return userObject;

# Restricted Routes
@app.route('/edit')
@loginRequired_decorator
@elevatedAction_decorator
def elevatedEditIndexView():
    # todo.

    if not g.user.is_elevated:
        return abort(404);  # to make it seem it doesn't exist

    if RoleTable.returnRoleIDByUsername(session[CURRENT_USER_KEY]) == 1:
        return redirect(url_for('editUsernameDatabase'));   # admin
    elif RoleTable.returnRoleIDByUsername(session[CURRENT_USER_KEY]) == 2:
        return redirect(url_for(''));   # rescue organization
    
    return abort(404);  # to make it seem it doesn't exist

@app.route('/<username>/addpet', methods=['GET', 'POST'])
@loginRequired_decorator
@rescueOrganizationAction_decorator
def rescueOrganizeAddPetView(username):
    # todo.
    return;

@app.route('/<username>/editPet/<int:petID>/', methods=['GET', 'POST'])
@loginRequired_decorator
@rescueOrganizationAction_decorator
def rescueOrganizeEditPetView(petID):
    # todo.
    # match username to pet to authorize
    return;

@app.route('/admin/users')
@loginRequired_decorator
@adminAction_decorator
def editUsernameDatabase():
    # todo.
    return;

@app.route('/admin/pets')
@loginRequired_decorator
@adminAction_decorator
def editPetDatabase():
# for admins, they can edit users except for other admins.
    # todo.
    return;



# tease with messages.

''' API Routes
'''
@app.route('/api/breeds/<int:petSpecieID>')
def fetchPetBreeds(petSpecieID):

    validPetBreeds = [];
    validPetBreeds.append({'id': DEFAULT_CHOICE_TUPLE[0], 'breed_name': DEFAULT_CHOICE_TUPLE[1]});
        # key is the text to dispaly, value is the option value because otherwise the reverse dict doesn't work (unless stringified)

    petSpecieObject = PetSpecie.returnPetSpecieByID(petSpecieID);

    if not petSpecieObject:
        return abort(404);

    if petSpecieID == 0 or petSpecieID >= 100:
        return jsonify({'breeds': validPetBreeds});
    
    petQueryMapping = {
        'Dog': Breed.returnAllDogBreeds(),
        'Cat': Breed.returnAllCatBreeds()
    };

    petBreedQuery = petQueryMapping[f'{petSpecieObject.specie_name}'];

    for petBreed in petBreedQuery:
        validPetBreeds.append({'id':petBreed.id, 'breed_name':petBreed.breed_name});

    return jsonify({'breeds': validPetBreeds});