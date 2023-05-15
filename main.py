# Libraries
from functools import wraps;
import random;
import string;
import os;
# Flask Core
from flask import Flask, current_app;
from flask import request, session, g, jsonify, render_template, redirect, url_for, flash, abort;
from sqlalchemy.exc import IntegrityError, InvalidRequestError;
# Modules
import models;
import forms;

# from models import db, connectDatabase;
# from models import User, Pet;
# from models import RoleTable, PetUserJoin, Breed, PetSpecie, CoatDescription, Color;
# from forms import LoginForm, RegisterForm, RequestElevatedForm, , AddEditPetForm, SearchPetForm;
# from forms import DeletePetForm;
# from wtforms.compat import iteritems, itervalues;
from wtforms.validators import InputRequired;
from flask_debugtoolbar import DebugToolbarExtension;
from markupsafe import Markup;
    # lmao, this is really a stopgap implementation of the app...

# Constants
CURRENT_USER_KEY = "currentUser";
RETURN_PAGE_KEY = "previousPage";

# Security
OBFUSCATION_STRING_KEY = 'obfuscationString';
OBFUSCATION_STRING_LENGTH = 9;
    # gibberish to change the session key every request
    # apparently the only way to prevent cookie forging is SSL and expecting the user to clear the cookies.
        # Flask Session Cookies can be easily decrypted: https://www.youtube.com/watch?v=mhcnBTDLxCI

# Search Constants
DEFAULT_CHOICE_TUPLE = (0, 'All');
BREED_CHOICE_TUPLE = (0, 'Not Available or Any');
DEFAULT_SEARCH_KWARG = {'gender':0, 'pet_specie':0};
    # set search parameters for 'gender' and 'pet_specie' to 'all' by default

app = Flask(__name__);

with app.app_context():
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///sb_29_capstone_project_petsearch');
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False; 
    app.config['SQLALCHEMY_ECHO'] = False;

    # Configure Sessions (req. for Debug Toolbar)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'afsd');

    # Configure Debug Toolbar
    # app.debug = True;
    app.debug = False;
    toolbar = DebugToolbarExtension(app);
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False;

    # Make it easier to debug on CLI
    import logging;
    log = logging.getLogger('werkzeug');
    log.setLevel(logging.ERROR);
        # purpose is to suppress all the GET requests for resources that is time consuming to scroll through

    models.connectDatabase(app);
    models.db.create_all();


'''HELPER FUNCTIONS'''
# User Authentication Helper Function(s)
def login(userObject):
    '''Log in user.'''

    session[CURRENT_USER_KEY] = userObject.username;

def logout():
    '''Logout user.'''

    if session:
        session.clear();

def authenticate(claimedUsername):
    '''Authenticate that the user in session is the same.'''

    if g.user == models.User.returnUserbyUsername(claimedUsername):
        return True;

    return abort(403);

def generateObfuscationString(stringLength):
    '''Obfuscates the session key if intercepted and generates a new one every time.'''

    obfuscatedString = ''.join(random.choice(string.printable) for index in range(stringLength));
    return obfuscatedString;

# Form Generation Helper Function(s)
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

    # Pet Gender
    petGenderChoices = [DEFAULT_CHOICE_TUPLE, (2, 'Male'), (1, 'Female')];
    petForm.gender.choices = petGenderChoices;

    # Pet Specie
    petSpecieChoices = [DEFAULT_CHOICE_TUPLE];
    databasePetSpecies = models.PetSpecie.returnAllSpecies();
    for specie in databasePetSpecies:
        petSpecieChoices.append((specie.id, Markup(specie.specie_fa)));
            # Otherwise Jinja yields 'too many values to unpack' error.

    petForm.pet_specie.choices = petSpecieChoices;
        # todo: make it inline; change to icons?
    

    # Pet Breed
    petBreedChoices = [BREED_CHOICE_TUPLE];
    databaseBreedTypes = models.Breed.returnAllBreeds();
    for databaseBreedType in databaseBreedTypes:
        petBreedChoices.append((databaseBreedType.id, databaseBreedType.breed_name));
    petForm.primary_breed.choices = petBreedChoices;
    # Work-around setting validate_choice = False; ~get init value of pet_specie and ???~
        # this is okay because the javascript will immediately reset the selectable choices

    # Pet Coat, Hair Type
    petHairChoices = [DEFAULT_CHOICE_TUPLE];
    databaseHairTypes = models.CoatDescription.returnAllHairTypes();
    for databaseHairType in databaseHairTypes:
        petHairChoices.append((databaseHairType.id, databaseHairType.coat_description));

    petForm.coat_hair.choices = petHairChoices;

    # Pet Coat, Coat Type
    petCoatChoices = [DEFAULT_CHOICE_TUPLE]; 
    databaseCoatPatterns = models.CoatDescription.returnAllCoatTypes();
    for databaseCoatPattern in databaseCoatPatterns:
        petCoatChoices.append((databaseCoatPattern.id, databaseCoatPattern.coat_description));

    petForm.coat_pattern.choices = petCoatChoices;

    # Pet Color, Light
    petLightColorChoices = [DEFAULT_CHOICE_TUPLE];
    databaseLightPetColors = models.Color.returnAllLightColors();
    for lightPetColor in databaseLightPetColors:
        petLightColorChoices.append((lightPetColor.id, lightPetColor.color_name));
        
    petForm.primary_light_shade.choices = petLightColorChoices;

    # Pet Color, Dark
    petDarkColorChoices = [DEFAULT_CHOICE_TUPLE];
    databaseDarkPetColors = models.Color.returnAllDarkColors();
    for databaseDarkPetColor in databaseDarkPetColors:
        petDarkColorChoices.append((databaseDarkPetColor.id, databaseDarkPetColor.color_name));
        # darkPetColors.append([(color.id, color) for color in models.Color.returnAllDarkColors()]);
            # Jinja yields 'too many values to unpack' error.
    
    petForm.primary_dark_shade.choices = petDarkColorChoices;

    return petForm;

def modifyPetFormSelection(petForm, petFormType = 'addEditPet'):

    if petFormType == 'addEditPet':

        if petForm.gender.choices:
            petForm.gender.choices.pop(0);

        if petForm.pet_specie.choices:
            petForm.pet_specie.choices.pop(0);

        if petForm.coat_hair.choices:
            petForm.coat_hair.choices.pop(0);

        if petForm.coat_pattern.choices:
            petForm.coat_pattern.choices.pop(0);

        if petForm.primary_light_shade.choices:
            petForm.primary_light_shade.choices.pop(0);

        if petForm.primary_dark_shade.choices:
            petForm.primary_dark_shade.choices.pop(0);

        return;

    return; 

def returnSearchPetForm(defaultSearchArguments = DEFAULT_SEARCH_KWARG):
    '''Returns a search Pet form for the index and search views.'''

    searchPetForm = forms.SearchPetForm(meta={'csrf': False}, **defaultSearchArguments);
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

        for fieldValidator in fieldValidators:
 
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

# Database Helper Function(s)
def returnSiteStatistics():
    ''''''

    statistics = {
        'users': models.User.returnNumberOfUsers(),
        'rescueOrganizations': models.RoleTable.returnNumberOfRescueOrganizations(),
        'pets': models.Pet.returnNumberOfPets(), 
    };

    return statistics;

'''DECORATORS'''
# Before & After Decorators
@app.before_request
def before_request():
    '''Before each request:
        - Obfuscate the encrypted session cookie by injecting random information.
        - Update g.user from session.
        - Get the referring page for a possible return route if landing on an error. (Perfection needed in a soft error w/ ...query.get() instead of ...query.get_or_404() but ¯\_(ツ)_/¯ for now)
        '''

    session[OBFUSCATION_STRING_KEY] = generateObfuscationString(OBFUSCATION_STRING_LENGTH);
        # obfuscation test. yes it will store extra data and obfuscate the original key because session is a dict itself.
    # update current user
    if CURRENT_USER_KEY in session:
        g.user = models.User.returnUserbyUsername(session[CURRENT_USER_KEY]);

    else:
        g.user = None;

    session[RETURN_PAGE_KEY] = request.referrer;
        # https://stackoverflow.com/a/39777426
        # need the 200 referrer, not the redirect referrrer

@app.after_request
def after_request(req):
    '''After each request:
        - Add non-caching headers.
        '''
        
    #   Turn off all caching in Flask: (useful for dev; in production, this kind of stuff is typically handled elsewhere)
    #       https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate";
    req.headers["Pragma"] = "no-cache";
    req.headers["Expires"] = "0";
    req.headers['Cache-Control'] = 'public, max-age=0';
    return req;

# Authentication Decorators
def loginRequired_decorator(f):
    ''''''
    @wraps(f)
    def wrapper(*args, **kwargs):

        if not g.user:
            flash("Access unauthorized.", "danger");
            return redirect(url_for('indexView'));
            
        return f(*args, **kwargs);
    
    return wrapper;

def logoutRequired_decorator(f):
    ''''''
    @wraps(f)
    def wrapper(*args, **kwargs):
        
        if g.user:
            flash("You must logout first.", "danger");
            return redirect(url_for('indexView'));
            
        return f(*args, **kwargs);
    
    return wrapper;

# ?????
"""def privateAuthentication_decorator(f):
    ''''''
    # troll idea: see if i can put a decorator before this one :P
    @wraps(f)
    def wrapper(*args, **kwargs):

        # authenticate helpermethod
        return f(*args, **kwargs);
    
    return wrapper;"""

def elevatedAction_decorator(f):
    ''''''
    @wraps(f)
    def wrapper(*args, **kwargs):

        if not g.user.is_elevated:
            return abort(404);
            # hide any authorized methods.
        
        return f(*args, **kwargs);
    
    return wrapper;

def rescueOrganizationAction_decorator(f):
    ''''''
    # troll idea: see if i can put a decorator before this one :P
    @wraps(f)
    def wrapper(*args, **kwargs):
        
        if not models.RoleTable.returnRoleIDByUsername(g.user.username).role_id == 2:
            return abort(404);
            # hide any authorized methods.

        return f(*args, **kwargs);
    
    return wrapper;

def adminAction_decorator(f):
    ''''''
    @wraps(f)
    def wrapper(*args, **kwargs):
        # authenticate helpermethod
        
        if not models.RoleTable.returnRoleIDByUsername(g.user.username).role_id == 1:
            return abort(404);
            # hide any authorized methods.

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
    ''''''

    searchPetForm = returnSearchPetForm();

    return render_template('index.html',
        form = searchPetForm, formType = 'search', 
        statistics=returnSiteStatistics());

@app.route('/search')
def searchView():
    ''''''
    
    # print('----------------------------');
    # print(request.args);

    if request.args:

        cleanedSearchArguments = models.Pet.cleanRequestData(request.args, requestType = 'searchQuery');
        # print('----------------------------');
        # print(cleanedSearchArguments)

        searchPetForm = returnSearchPetForm(request.args);

    return render_template('search.html',
        form = searchPetForm, formType='search',
        petList = models.Pet.returnPetSearchQuery(request.args));

@app.route('/pets/<int:petID>')
def petView(petID):
    ''''''

    petObject = models.Pet.returnPetByID(petID);
    petCoatInformation = [
            models.CoatDescription.gracefullyReturnCoatDescriptionById(petObject.coat_hair).coat_description,
            models.CoatDescription.gracefullyReturnCoatDescriptionById(petObject.coat_pattern).coat_description,
            models.Color.gracefullyReturnColorByColorID(petObject.primary_light_shade).color_name,
            models.Color.gracefullyReturnColorByColorID(petObject.primary_dark_shade).color_name
        ];
            #   [CoatDescription(Hair Type), CoatDescription(Coat Pattern), Color (Light), Color (Dark)]
            #   a bit late to realize DB design short-sighted-ness of the drawbacks of implementing a non-join M-N relationship to avoid a limited number of Join entries since references break.
            #   basically a work around for now

    return render_template('pet/profile.html',
        petObject = petObject, petCoatInformation = petCoatInformation);

# General Public Exclusive Routes
@app.route('/login', methods=['GET', 'POST'])
@logoutRequired_decorator
def loginView():
    ''''''

    loginForm = forms.LoginForm();

    if loginForm.validate_on_submit():
        

        if not models.User.gracefullyReturnUserByUsername(request.form.get('username')):

            #don't give more information
            loginForm.encrypted_password.errors = ['Incorrect username/password combination.'];
            return render_template('onboarding.html',
                form=loginForm, onboardingAction='login',
                statistics=returnSiteStatistics());

        userObject = models.User.authentication(request.form.get('username'), request.form.get('encrypted_password'));

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
    ''''''

    registerForm = forms.RegisterForm();

    if registerForm.validate_on_submit():

        try:

            userObject = models.User.createUser(request.form);
            models.db.session.commit();
                
            ''' except InvalidRequestError:

                # SQLAlchemy raises `InvalidRequestError` instead of `IntegrityError`,  if no commit, for violating UNIQUE constraint
                
                registerForm.username.errors = ['Username already taken.'];
                
                # a redirect will smother the error
                return render_template('onboarding.html',
                    form=registerForm, onboardingAction='signup',
                    statistics=returnSiteStatistics());'''

        except IntegrityError:

            models.db.session.rollback();
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
    ''''''

    organizationRequestForm = forms.RequestElevatedForm();

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
    ''''''
    logout();
    return redirect(url_for('indexView'));

# User Routes
@app.route('/users/<username>')
def userView(username):
    ''''''

    userObject = models.User.returnUserbyUsername(username);

    favoritePets = fetchUsersFavoritePetList(username);

    return render_template('user/profile.html',
        userObject = userObject,
        petList = favoritePets);

@app.route('/users/<username>/edit', methods=['GET', 'POST'])
@loginRequired_decorator
def editUserView(username):
    ''''''

    # next up how to wrap the following 2 lines in a decorator:
    userObject = models.User.returnUserbyUsername(username);
    authenticate(userObject.username);

    editUserForm = forms.EditUserForm(**(userObject.returnInstanceAttributes()));

    if editUserForm.validate_on_submit():

        if models.User.authentication(username, request.form.get('password')):
            # user username to "double" authentication
            userObject.updateUser(request.form);
            return redirect(url_for('userView', username=username));

        else:

            editUserForm.password.errors=['Invalid Password. Try again.'];
            return render_template('user/edit.html',
                form=editUserForm, 
                userObject = userObject);

    return render_template('user/edit.html',
        form=editUserForm, 
        userObject = userObject);

# Restricted Routes
@app.route('/edit')
@loginRequired_decorator
@elevatedAction_decorator
def elevatedEditIndexView():
    ''''''

    if models.RoleTable.returnRoleIDByUsername(g.user.username).role_id == 1:
        return redirect(url_for('editUsernameDatabase'));   # admin
    elif models.RoleTable.returnRoleIDByUsername(g.user.username).role_id == 2:
        return redirect(url_for('rescueOrganizeIndexView'));   # rescue organization
    
    return abort(404);  # to make it seem it doesn't exist

@app.route('/dashboard', methods=['GET', 'POST'])
@loginRequired_decorator
@rescueOrganizationAction_decorator
def rescueOrganizeIndexView():
    ''''''
    # not within project scope: overview of authorized users to maintain the rescue agency's database
    
    petList = models.PetUserJoin.returnPetsByUsername(g.user.username);

    return render_template('admin/databaseView.html',
        listedInformation = petList,
        informationType = ['rescue']);

@app.route('/dashboard/addpet', methods=['GET', 'POST'])
@loginRequired_decorator
@rescueOrganizationAction_decorator
def rescueOrganizeAddPetView():
    ''''''
    # todo.

    addPetForm = forms.AddEditPetForm();
    populatePetFormSelectFields(addPetForm);
    modifyPetFormSelection(addPetForm);

    if addPetForm.validate_on_submit():

        models.Pet.createPet(request.form, userUsername = g.user.username);
        return redirect(url_for('rescueOrganizeIndexView'));

    return render_template('pet/addEdit.html',
        form=addPetForm, formType='addPet');

@app.route('/pets/<int:petID>/edit', methods=['GET', 'POST'])
@loginRequired_decorator
@rescueOrganizationAction_decorator
def rescueOrganizeEditPetView(petID):
    ''''''

    # next up how to wrap the following 2 lines in a decorator:
    if not models.PetUserJoin.authenticatePetEdit(g.user.username, petID):
        return abort(403);

    petObject = models.Pet.returnPetByID(petID);

    editPetForm = forms.AddEditPetForm(**(petObject.returnInstanceAttributes()));

    populatePetFormSelectFields(editPetForm);
    modifyPetFormSelection(editPetForm);

    if editPetForm.validate_on_submit():
        # print(request.form);
        models.Pet.updatePet(request.form, petObject);
        return redirect(url_for('rescueOrganizeIndexView'));

    return render_template('pet/addEdit.html',
        form=editPetForm, formType='editPet',
        petObject=petObject);

# Too ambitious this late into the project.
'''@app.route('/pets/<int:petID>/delete', methods=['POST'])
@loginRequired_decorator
@elevatedAction_decorator
def deletePetView(petID):
    # this was an after-thought ._.

    deletePetForm = DeletePetForm();

    if deletePetForm.validate_on_submit():
        if models.RoleTable.returnRoleIDByUsername(g.user.username).role_id == 1:
            print(request.form);
            return redirect(url_for('editPetDatabase'));
        elif models.RoleTable.returnRoleIDByUsername(g.user.username).role_id == 2 and models.PetUserJoin.authenticatePetEdit(g.user.username, petID):
            print(petID);
            print(request.form);
            return redirect(url_for('rescueOrganizeIndexView'))
    
        abort(404);
            # hide this route from the public
    
    return()'''

@app.route('/pets/<int:petID>/delete', methods=['GET'])
@loginRequired_decorator
@elevatedAction_decorator
def deletePetView(petID):
    # this was an after-thought ._.

    if models.RoleTable.returnRoleIDByUsername(g.user.username).role_id == 1:
        models.Pet.deletePet(petID);
        return redirect(url_for('editPetDatabase'));
    elif models.RoleTable.returnRoleIDByUsername(g.user.username).role_id == 2 and models.PetUserJoin.authenticatePetEdit(g.user.username, petID):
        models.Pet.deletePet(petID);
        return redirect(url_for('rescueOrganizeIndexView'))
    
    return abort(404);
        # hide this route from the public

@app.route('/database/users')
@loginRequired_decorator
@adminAction_decorator
def editUsernameDatabase():
    ''''''

    # for admins, they can take action against any user(s) except other admins.
    userList = models.User.returnAllNonAdminUsers();

    return render_template('admin/databaseView.html',
        listedInformation = userList,
        informationType = ['admin', 'users']);

@app.route('/database/pets')
@loginRequired_decorator
@adminAction_decorator
def editPetDatabase():
    ''''''

    petList = models.Pet.returnAllPets();

    return render_template('admin/databaseView.html',
        listedInformation = petList,
        informationType = ['admin', 'pets']);

# tease with messages.

''' API Routes & API Helper Methods
'''
def json_serializeSQLAModel(SQLAModelObject):
    ''''''

    modelProperties = vars(SQLAModelObject);
    modelProperties.pop('_sa_instance_state');

    return modelProperties;

def json_returnSerializedPetList(petObjectList):
    
    petListSerialized = [json_serializeSQLAModel(petObject) for petObject in petObjectList];

    return petListSerialized;

def fetchUsersFavoritePetList(username):
    ''''''

    userObject = models.User.returnUserbyUsername(username);
    
    if userObject.is_elevated and (models.RoleTable.returnRoleIDByUsername(username).role_id == 2):
        
        favoritePets = [petUserObject.petReference for petUserObject in models.PetUserJoin.returnPetsByUsername(username)];

        return favoritePets;

    return None; # {'This is implemented later': 'for non-rescue organizations'};

def serializeUsersFavoritePetList(username):
    ''''''

    userObject = models.User.returnUserbyUsername(username);
    favoritePets = [];
    
    if userObject.is_elevated and (models.RoleTable.returnRoleIDByUsername(username).role_id == 2):
        
        petObjectList = fetchUsersFavoritePetList(username);
        favoritePets.append(json_returnSerializedPetList(petObjectList));

        return favoritePets;

    return None; # {'This is implemented later': 'for non-rescue organizations'};

@app.route('/api/search')
def fetchSearchQuery():
    # todo? maybe no API search.
    return;

@app.route('/api/breeds/<int:petSpecieID>')
def fetchPetBreeds(petSpecieID):
    ''''''
    validPetBreeds = [];
    validPetBreeds.append({'id': BREED_CHOICE_TUPLE[0], 'breed_name': str(BREED_CHOICE_TUPLE[1])});
        # key is the text to dispaly, value is the option value because otherwise the reverse dict doesn't work (unless stringified)

    petSpecieObject = models.PetSpecie.returnPetSpecieByID(petSpecieID);

    if not petSpecieObject:
        return abort(404);

    if petSpecieID == 0 or petSpecieID >= 100:
        return jsonify({'breeds': validPetBreeds});
    
    petQueryMapping = {
        'Dog': models.Breed.returnAllDogBreeds(),
        'Cat': models.Breed.returnAllCatBreeds()
    };
        # inconvenient for maintenance. maybe fix

    petBreedQuery = petQueryMapping[f'{petSpecieObject.specie_name}'];

    for petBreed in petBreedQuery:
        validPetBreeds.append({'id':petmodels.Breed.id, 'breed_name':petmodels.Breed.breed_name});

    return jsonify({'breeds': validPetBreeds});

@app.route('/api/<username>/pets')
def fetchUserPetList(username):
    ''''''
    favoritePets = fetchUsersFavoritePetList(username);
    return jsonify({'favoritePets': favoritePets});

@app.route('/health/')
def renderHealthCheck():
    return "OK";

if __name__ == "__main__":
    app.run();
	# app.run(debug=True);