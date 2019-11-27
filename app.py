from flask import Flask, render_template, flash, redirect, url_for, sessions, logging, request
import pymysql.cursors
from hashlib import sha3_256
from sys import getsizeof

from Models import UserForms

from Models.UserForms import RegisterForm, LoginForm

connection = pymysql.connect(host='localhost',
                             user='oscar',
                             password='hejsan123',
                             db='BookCommerce',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

"""
try:
    with connection.cursor() as cursor:
        # Create a new record
        sql = "CREATE TABLE Employee(id int, LastName varchar(32), FirstName varchar(32), DepartmentCode int)"
        cursor.execute(sql)
    connection.commit()
finally:
    connection.close()
"""
app = Flask(__name__)
app.secret_key = 'a4b99086395b5b714fb1856c1d6cd709'

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if (request.method == 'POST') and form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        address = form.address.data
        country = form.country.data
        salt = form.salt
        password = sha3_256((form.password.data+form.salt).encode()).hexdigest()
        email = form.email.data
        city = form.city.data
        postal_code = int(form.postal_code.data)
        phone = int(form.phone.data)
        try:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO User (Email, Hash, Salt, FirstName, LastName, City, PostalCode, Country, Phone, Address, Privilege, AccountBalance) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, (email, password, salt, first_name, last_name, city, postal_code, country, phone, address, 1, 500))
            connection.commit()
        finally:
            connection.close()
        flash('Account created!')
        return redirect(url_for('index'))


    else:
        return render_template('register.html', form=form)

@app.route('/login')
def login():
    form = LoginForm()
    return render_template(login.html, title='Login', form=form)

if __name__ == '__main__':
    app.run(Debug=True)
