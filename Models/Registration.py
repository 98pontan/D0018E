from flask import Flask, render_template, flash, redirect, url_for, sessions, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
import hashlib, uuid


class RegisterForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=50), validators.InputRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=50), validators.InputRequired()])
    email = StringField('Email', [validators.Email("Enter a valid email"), validators.Length(min=1, max=50), validators.InputRequired()])
    city = StringField('City', [validators.Length(min=1, max=50), validators.InputRequired()])
    postal_code = StringField('Postal Code', [validators.Length(min=5, max=5), validators.InputRequired()])
    phone = StringField('Phone Number', [validators.Length(min=1, max=50)])
