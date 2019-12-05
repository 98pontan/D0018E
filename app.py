from datetime import timedelta

from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, g
import pymysql.cursors
import pymysql
from hashlib import sha3_256
from functools import wraps
from Models import UserForms

from Models.UserForms import RegisterForm, LoginForm, EditAccountForm

app = Flask(__name__)
app.secret_key = 'a4b99086395b5b714fb1856c1d6cd709'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            # return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index'))

    return decorated_function


@app.route('/')
@app.route('/index')
def index():
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # get categories
            cursor.execute("SELECT * FROM Category;")
            connection.commit()
            categories = cursor.fetchall()

            #get "new releases"
            cursor.execute("SELECT * FROM Product ORDER BY Product_ID DESC LIMIT 3;")
            connection.commit()
            products = cursor.fetchall()

    finally:
        connection.close()
    print(type(categories))
    return render_template('index.html', categories=categories, products=products)


# register
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
                cursor.execute(sql, (
                    email, password, salt, first_name, last_name, city, postal_code, country, phone, address, 1, 500))
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
                sql = "SELECT User.User_ID, User.Hash, User.Salt FROM User WHERE User.Email = %s;"
                result = cursor.execute(sql, email)
            connection.commit()
        finally:
            connection.close()
        if result >= 1:
            data = cursor.fetchone()
            hash = data['Hash']
            salt = data['Salt']
            password = sha3_256((form.password.data + salt).encode()).hexdigest()
            if password == hash:
                print("password correct")
                session.permanent = True    #Makes the login valid for 5 minutes as set in config
                session['logged_in'] = True
                session['salt'] = data['Salt']
                session['user_id'] = data['User_ID']
                flash('You are now logged in!', 'success')
                return redirect(url_for('index'))
            else:
                error = "Password incorrect"
                return render_template('login.html', error=error, form=form)
                print("password incorrect")
        else:
            error = "Username incorrect"
            return render_template('login.html', error=error, form=form)
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))


@app.route('/myaccount')
@login_required
def myaccount():
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "SELECT User.AccountBalance, User.Address, User.City, User.Country, User.Email, User.FirstName, User.LastName, User.Phone, User.PostalCode FROM User WHERE User.User_ID = %s;"
            cursor.execute(sql, session['user_id'])
        connection.commit()
    finally:
        connection.close()
    data = cursor.fetchone()
    print(session['user_id'])
    print(data)
    return render_template('myaccount.html', values=data)

@app.route('/myaccount/edit', methods=['GET', 'POST'])
@login_required
def editaccount():
    form = EditAccountForm(request.form)
    user_id = session['user_id']
    address = form.address.data
    city = form.city.data
    country = form.country.data
    postal_code = form.postal_code.data
    phone = form.phone.data
    salt = form.salt
    password = sha3_256((form.password.data + salt).encode()).hexdigest()
    if request.method == 'POST' and form.validate():
        connection = pymysql.connect(host='localhost',
                                     user='oscar',
                                     password='hejsan123',
                                     db='BookCommerce',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "UPDATE User SET User.City = %s, User.Address = %s, User.Phone = %s, User.PostalCode = %s, User.Country = %s, User.Hash = %s, User.Salt = %s WHERE User.User_ID = %s;"
                result = cursor.execute(sql, (city, address, phone, postal_code, country, password, salt, user_id))
            connection.commit()
        finally:
            connection.close()
        flash('Info changed!')
        return redirect(url_for('myaccount'))
    else:
        return render_template('editaccount.html', form=form)

# category
@app.route('/category')
# take in an id parameter but for now leave blank
def category(id):
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "SELECT * FROM Product WHERE Category_ID = id"
            result = cursor.execute(sql)
        connection.commit()

    finally:
        connection.close()
        if result >= 1:
            data = cursor.fetchall()
            return render_template('category.html', data=data)
#checkout
@app.route('/checkout')
def checkout():
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql0 = "SELECT CartItem.Product_ID, CartItem.Quantity, Product.Author FROM CartItem, Cart, Product WHERE Cart.Cart_ID=CartItem.Cart_ID AND Cart.User_ID= %s AND CartItem.Product_ID=Product.Product_ID;"
            cursor.execute(sql0, session['user_id'])
        connection.commit()

    finally:
        connection.close()
    data = cursor.fetchall()
    print(data)
    return render_template('checkout.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
