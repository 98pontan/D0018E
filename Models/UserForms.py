from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SubmitField
from secrets import token_hex

from wtforms.validators import InputRequired, Length, Email


class RegisterForm(Form):
    first_name = StringField('First Name', validators=[Length(min=1, max=50), InputRequired()])
    last_name = StringField('Last Name', validators=[Length(min=1, max=50), InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=50)])
    salt = token_hex(16)
    address = StringField('Address', validators=[InputRequired(), Length(min=1, max=50)])
    country = StringField('Country', validators=[InputRequired(), Length(min=1, max=50)])
    email = StringField('Email', validators=[InputRequired(), Length(min=1, max=50), Email()])
    city = StringField('City', validators=[InputRequired(), Length(min=1, max=50)])
    postal_code = StringField('Postal Code', validators=[InputRequired(), Length(min=5, max=5)])
    phone = StringField('Phone Number', validators=[Length(min=1, max=50)])
    submit = SubmitField('Sign Up')


class LoginForm(Form):
    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


class EditAccountForm(Form):
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=50)])
    salt = token_hex(16)
    address = StringField('Address', validators=[InputRequired(), Length(min=1, max=50)])
    country = StringField('Country', validators=[InputRequired(), Length(min=1, max=50)])
    city = StringField('City', validators=[InputRequired(), Length(min=1, max=50)])
    postal_code = StringField('Postal Code', validators=[InputRequired(), Length(min=5, max=5)])
    phone = StringField('Phone Number', validators=[Length(min=1, max=50)])
    submit = SubmitField('Submit changes')
