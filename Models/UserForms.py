from flask import Flask, render_template, flash, redirect, url_for, sessions, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SubmitField
import hashlib, uuid

from wtforms.validators import InputRequired, Length, Email


class RegisterForm(Form):
    first_name = StringField('First Name', validators=[Length(min=1, max=50), InputRequired()])
    last_name = StringField('Last Name', validators=[Length(min=1, max=50), InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=50)])
    email = StringField('Email', validators=[InputRequired(), Length(min=1, max=50), Email()])
    city = StringField('City', validators=[InputRequired(), Length(min=1, max=50)])
    postal_code = StringField('Postal Code', validators=[InputRequired(), Length(min=5, max=5)])
    phone = StringField('Phone Number', validators=[Length(min=1, max=50)])
    submit = SubmitField('Sign Up')

class LoginForm(Form):
    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Email', validators=[InputRequired()])
    submit = SubmitField('Login')