from flask import Flask, render_template, flash, redirect, url_for, sessions, logging, request
import pymysql.cursors
from Models import Registration
from wtforms import Form, StringField, TextAreaField, PasswordField, validators

from Models.Registration import RegisterForm

"""connection = pymysql.connect(host='localhost',
                             user='oscar',
                             password='hej',
                             db='BookCommerce',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        # Create a new record
        sql = ""#"CREATE TABLE Employee(id int, LastName varchar(32), FirstName varchar(32), DepartmentCode int)"
        cursor.execute(sql)
    connection.commit()
finally:
    connection.close()
"""
app = Flask(__name__)


@app.route('/')
@app.route('/index')
def hello_world():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.form == 'POST' and form.validate():
        return render_template('register.html', form=form)
    return render_template('register.html', form=form)



if __name__ == '__main__':
    app.run(Debug=True)
