from flask import Flask, render_template, flash, redirect, url_for, sessions, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
import hashlib, uuid

class ReigsterForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=50), validators.InputRequired])
    last_name = StringField('Last Name', [validators.Length(min=1, max=50), validators.InputRequired()])
    email = StringField('Email', [validators.email, validators.Length(min=1, max=50)])
    city = StringField('City', validators.Length(min=1, max=50))
    postal_code = StringField('Postal Code', validators.Length(min=1, max=50))
    phone = StringField('Phone Number', validators.Length(min=1, max=50))