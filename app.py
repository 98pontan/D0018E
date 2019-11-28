from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
import pymysql.cursors
from hashlib import sha3_256
from Models import UserForms

from Models.UserForms import RegisterForm, LoginForm

"""
connection = pymysql.connect(host='localhost',
                             user='oscar',
                             password='hej',
                             db='BookCommerce',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

"""
app = Flask(__name__)
app.secret_key = 'a4b99086395b5b714fb1856c1d6cd709'


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

#register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if (request.method == 'POST') and form.validate():
        print("yes")
        first_name = form.first_name.data
        last_name = form.last_name.data
        address = form.address.data
        country = form.country.data
        salt = form.salt
        password = sha3_256((form.password.data + form.salt).encode()).hexdigest()
        email = form.email.data
        city = form.city.data
        postal_code = int(form.postal_code.data)
        phone = int(form.phone.data)
        connection = pymysql.connect(host='localhost',
                                     user='oscar',
                                     password='hejsan123',
                                     db='BookCommerce',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if (request.method == 'POST') and form.validate():
        email = form.email.data
        connection = pymysql.connect(host='localhost',
                                     user='oscar',
                                     password='hejsan123',
                                     db='BookCommerce',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "SELECT User.Hash, User.Salt FROM User WHERE User.Email = %s;"
                result = cursor.execute(sql, (email))
            connection.commit()
        finally:
            connection.close()
        if (result >= 1):
            data = cursor.fetchone()
            hash = data['Hash']
            salt = data['Salt']
            password = sha3_256((form.password.data + salt).encode()).hexdigest()
            if(password == hash):
                print("password correct")
                return redirect(url_for('index'))
            else:
                error = "Password incorrect"
                return render_template('login.html', error=error, form=form)
                print("password incorrect")
        else:
            error = "Username incorrect"
            return render_template('login.html', error=error, form=form)
    return render_template('login.html', title='Login', form=form)


#category
@app.route('/category')
def category(id):
    #create cursor
    cur = pymysql.connection.cursor()

    #get books
    result = cur.execute("SELECT * FROM Product WHERE Category_ID = id ")
    categories = cur.fetchall()

    return render_template('category.html', categories= categories)



if __name__ == '__main__':
    app.run(debug=True)