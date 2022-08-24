from flask_wtf import FlaskForm;
from wtforms import StringField, #...;
    # Common Imports: StringField, TextAreaField, IntegerField, BooleanField, RadioField, HiddenField, PasswordField
from wtforms.validators import InputRequired, Optional, Length;

class LoginForm(FlaskForm):
    pass;

class RegisterForm(LoginForm):
    pass;

class AddEditPetForm(AddPetForm):
    pass;
    