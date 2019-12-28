from datetime import timedelta

from click.utils import PacifyFlushWrapper
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, g
import pymysql.cursors
import pymysql
from hashlib import sha3_256
from functools import wraps
from Models import UserForms
from Models.AdminForms import CreateProduct, CreateCategory
from Models.ReviewForms import MakeReview

from Models.UserForms import RegisterForm, LoginForm, EditAccountForm, DeleteAccount

app = Flask(__name__)
app.secret_key = 'a4b99086395b5b714fb1856c1d6cd709'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            # return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        else:
            flash("Please login")
            return redirect(url_for('login'))

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session['privilege'] == 2:
            # return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index'))

    return decorated_function


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
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

            # get "new releases"
            cursor.execute("SELECT * FROM Product ORDER BY Product_ID DESC LIMIT 3;")
            connection.commit()
            products = cursor.fetchall()

    finally:
        connection.close()
    # print(type(categories))
    return render_template('index.html', categories=categories, products=products)


def createcart():
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `Cart`(`User_ID`) VALUES(%s);"
            cursor.execute(sql, (session['user_id']))

            sql2 = "SELECT Category.eNam FROM Category WHERE Category_ID = %s"
            result2 = cursor.execute(sql2, Category_ID)
            connection.commit()
            categoryName = cursor.fetchone()

        connection.commit()
    finally:
        connection.close()


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
        postal_code = form.postal_code.data
        phone = form.phone.data
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
                sql = "SELECT User.User_ID, User.Hash, User.Salt, User.Privilege, User.AccountBalance FROM User WHERE User.Email = %s;"
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
                session.permanent = True  # Makes the login valid for 5 minutes as set in config
                session['logged_in'] = True
                session['salt'] = data['Salt']
                session['user_id'] = data['User_ID']
                getCart_ID()
                session['privilege'] = data['Privilege']
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


@app.route('/myaccount/delete')
@login_required
def deleteaccount():
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "DELETE FROM User WHERE User.User_ID = %s;"
            cursor.execute(sql, session['user_id'])
        connection.commit()
    finally:
        connection.close()
    flash('Account Deleted!')
    session.clear()
    return redirect(url_for('index'))


@app.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin():
    create_product = CreateProduct(request.form)
    create_category = CreateCategory(request.form)
    if CreateProduct.validate and request.method == 'POST' and request.form['btn'] == 'Create Product':
        createproduct(create_product)
        flash('Product created!')
        return redirect(url_for('admin'))
    elif CreateCategory.validate and request.method == 'POST' and request.form['btn'] == 'Create Category':
        createcategory(create_category)
        flash('Category created!!')
        return redirect(url_for('admin'))
    elif request.method == 'GET':
        return render_template('admin.html', create_product=create_product, create_category=create_category)


def createcategory(create_category):
    name = create_category.name.data
    description = create_category.description.data
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = """INSERT INTO Category
                    (`Name`,
                    `Description`)
                    VALUES
                    (%s,
                    %s);"""
            cursor.execute(sql, (name, description))
        connection.commit()
    finally:
        connection.close()


def createproduct(create_product):
    category = request.form.get("selected_category")
    price = create_product.price.data
    discount = create_product.discount.data
    author = create_product.author.data
    description = create_product.description.data
    isbn = create_product.isbn.data
    title = create_product.title.data
    units_in_stock = create_product.units_in_stock.data
    language = create_product.language.data
    number_of_pages = create_product.number_of_pages.data
    publicer = create_product.publicer.data
    print(request.form.get("selected_category"))
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = """INSERT INTO Product
                      (`Category_ID`,
                      `Price`,
                      `Discount`,
                      `UnitsInStock`,
                      `Description`,
                      `ISBN`,
                      `Author`,
                      `Publicer`,
                      `NumberOfPages`,
                      `Language`,
                      `Title`)
                      VALUES
                      (%s, 
                      %s, 
                      %s, 
                      %s,
                      %s,
                      %s,
                      %s,
                      %s,
                      %s,
                      %s,
                      %s);"""
            cursor.execute(sql, (
                category, price, discount, units_in_stock, description, isbn, author, publicer, number_of_pages,
                language,
                title))
        connection.commit()
    finally:
        connection.close()


@app.route('/search', methods=['GET', 'POST'])
def search():
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        if request.method == "POST":
            book = request.form['book']
            # search with Title or Author
            sql = "SELECT Product.Title, Product.Author, Product.Price, Product.Product_ID FROM Product WHERE Title LIKE %s OR Author LIKE %s"
            cursor.execute(sql, (book, book))
            connection.commit()
            data = cursor.fetchall()
            if len(data)== 0 and book == 'all':
                cursor.execute("SELECT Product.Title, Product.Author, Product.Price, Product.Product_ID FROM Product")
                connection.commit()
                data = cursor.fetchall()
                print(data)
            return render_template('search.html', data=data)


        connection.close()
        return render_template('search.html')


# category
@app.route('/category/<int:Category_ID>', methods=['GET', 'POST'])
# take in an id parameter but for now leave blank
def category(Category_ID):
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:

            # get all products from Category
            sql = "SELECT * FROM Product WHERE Category_ID = %s"
            result = cursor.execute(sql, Category_ID)
            connection.commit()
            product = cursor.fetchall()

            # get category name
            sql2 = "SELECT Category.Name FROM Category WHERE Category_ID = %s"
            result2 = cursor.execute(sql2, Category_ID)
            connection.commit()
            categoryName = cursor.fetchone()

            # get category description
            sql3 = "SELECT Category.Description FROM Category WHERE Category_ID = %s"
            result3 = cursor.execute(sql3, Category_ID)
            connection.commit()
            categoryDesc = cursor.fetchone()

            #print("helo")
    except TypeError:
        print("typ error")
        return redirect(url_for('index'))
    finally:
        connection.close()
        if result >= 1 and result2 >= 1 and result3 >= 1:
            # print(categoryName)
            return render_template('category.html', product=product, categoryName=categoryName, categoryDesc=categoryDesc)
        elif result2 >= 1 and result3 >= 1:
            return render_template('category.html', categoryName=categoryName, categoryDesc=categoryDesc)
        else:
            return index();


# PRODUCT
@app.route('/product/<int:Product_ID>', methods=['GET', 'POST'])
# take in an id parameter but for now leave blank
def product(Product_ID):
    form = MakeReview(request.form)
    if (request.method == 'POST') and form.validate():
        print(Product_ID)
        makereview(Product_ID, form)
        return redirect(url_for('index'))
    else:
        reviews = getreviews(Product_ID)
        connection = pymysql.connect(host='localhost',
                                     user='oscar',
                                     password='hejsan123',
                                     db='BookCommerce',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)

        try:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "SELECT * FROM Product, Category WHERE Product.Product_ID = %s AND Category.Category_ID = Product.Category_ID "
                result = cursor.execute(sql, Product_ID)
                connection.commit()

        finally:
            connection.close()
            if result >= 1:
                data = cursor.fetchone()
                #   print(reviews)
                return render_template('product.html', data=data, form=form, reviews=reviews)


@login_required
def makereview(product_id, form):
    review = form.review.data
    rating = int(form.rating.data)
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # Create new record
            sql = """INSERT INTO `BookCommerce`.`Review`
                    (
                    `Product_ID`,
                    `Review`,
                    `Rating`,
                    `User_ID`)
                    VALUES
                    (%s, %s, %s, %s);"""
            cursor.execute(sql, (product_id, review, rating, session['user_id']))
            connection.commit()
    finally:
        connection.close()

def getreviews(product_id):
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            # Create new record
            sql = "SELECT Review.Review, Review.Rating, User.FirstName, User.LastName FROM Review, User WHERE Review.Product_ID = %s AND Review.User_ID = User.User_ID"
            cursor.execute(sql, product_id)
            connection.commit()
    finally:
        connection.close()
        data = cursor.fetchall()
        return data


@app.route('/addItem/<int:Product_ID>')
@login_required
def addItem(Product_ID):
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO CartItem(Product_ID, Quantity, Cart_ID) VALUES(%s, 1, %s);"
            cursor.execute(sql, (Product_ID, session['Cart_ID']))
        connection.commit()

    finally:
        connection.close()
        flash("Product added to cart")
        return redirect(url_for('category'))


# pre-checkout to add products to cart
@app.route('/addcheckout/<int:Product_ID>')
@login_required
def addCheckout(Product_ID):
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO CartItem(Product_ID, Quantity, Cart_ID) VALUES(%s, 1, %s);"
            cursor.execute(sql, (Product_ID, session['Cart_ID']))

        connection.commit()
    finally:
        connection.close()
        flash("Product added to cart")
        return redirect(url_for('checkout'))



#checkout
@app.route("/checkout", methods=['GET', 'POST'])
@login_required
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
            sql0 = "SELECT CartItem.Product_ID, CartItem.Quantity, Product.Author, Product.Title, Product.Price FROM CartItem, Cart, Product WHERE Cart.Cart_ID=CartItem.Cart_ID AND Cart.User_ID=%s AND CartItem.Product_ID=Product.Product_ID AND CartItem.Product_ID=Product.Product_ID AND CartItem.Product_ID=Product.Product_ID"

            cursor.execute(sql0, session['user_id'])
            connection.commit()
            data = cursor.fetchall()

    finally:
        connection.close()
        getAccountbalance()
        total_sum = totalsum(data)
    return render_template('checkout.html', data=data, accountBalance=session['accountbalance'], total_sum=total_sum)

def getAccountbalance():
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql0 = "SELECT User.AccountBalance FROM User WHERE User_ID = %s"
            cursor.execute(sql0, session['user_id'])
            connection.commit()
            data = cursor.fetchone()
            session['accountbalance'] = data['AccountBalance']
    finally:
        connection.close()


def totalsum(dict):
    total_price = 0
    for key in dict:
        total_price += key['Quantity'] * key['Price']
    return total_price


@app.route('/removeproduct/<int:Product_ID>')
@login_required
def removeproduct(Product_ID):
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql0 = "DELETE FROM CartItem WHERE Product_ID = %s AND Cart_ID = %s; "
            cursor.execute(sql0, (Product_ID, session['Cart_ID']))
        connection.commit()
    finally:
        connection.close()
    data = cursor.fetchall()
    flash("Product removed")
    return redirect(url_for('checkout'))


def getCart_ID():
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql0 = "SELECT Cart.Cart_ID FROM Cart WHERE  Cart.User_ID = %s"
            cursor.execute(sql0, session['user_id'])
        connection.commit()
    finally:
        connection.close()
    data = cursor.fetchone()
    # print(data['Cart_ID'])
    try:
        session['Cart_ID'] = data['Cart_ID']
    except TypeError:
        connection = pymysql.connect(host='localhost',
                                     user='oscar',
                                     password='hejsan123',
                                     db='BookCommerce',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)

        try:
            with connection.cursor() as cursor:
                sql0 = "INSERT INTO `BookCommerce`.`Cart`(`User_ID`)VALUES(%s);"
                cursor.execute(sql0, session['user_id'])
                sql1 = "SELECT Cart.Cart_ID FROM Cart WHERE  Cart.User_ID = %s"
                cursor.execute(sql1, session['user_id'])
            connection.commit()
        finally:
            connection.close()
            cart_data = cursor.fetchone()
            session['Cart_ID'] = cart_data['Cart_ID']


@app.route('/purchase/<int:total_sum>')
@login_required
def purchase(total_sum):
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:

            sql1 = "SELECT User.AccountBalance FROM User WHERE User_ID = %s"
            cursor.execute(sql1, session['user_id'])
            accountbalance = cursor.fetchall()
            connection.commit()
            AB = 0
            for i in accountbalance:
                AB = i['AccountBalance']
            print("tot_sum", total_sum)
            if(AB >= total_sum and total_sum > 0):
                newAB = AB - total_sum
                sql2 = "UPDATE User SET AccountBalance = %s WHERE User_ID = %s"
                cursor.execute(sql2, (newAB, session['user_id']))
                connection.commit()

                sql = "INSERT INTO Orders(Orders.User_ID, Orders.Phone, Orders.Address, Orders.City, Orders.PostalCode, Orders.Country) SELECT User.User_ID, User.Phone, User.Address, User.City, User.PostalCode, User.Country FROM User WHERE User.User_ID = %s;"
                cursor.execute(sql, session['user_id'])
                connection.commit()

                sql4 = "SELECT MAX(Orders.Order_ID) FROM Orders WHERE Orders.User_ID = %s;"
                cursor.execute(sql4, session['user_id'])
                connection.commit()
                data = cursor.fetchone()
                session['order_id'] = data['MAX(Orders.Order_ID)']

                sql5 = "INSERT INTO OrderProduct(OrderProduct.Order_ID, OrderProduct.Product_ID, OrderProduct.Quantity, OrderProduct.Price) SELECT %s, CartItem.Product_ID, CartItem.Quantity, Product.Price FROM CartItem, Product, Orders WHERE Orders.Order_ID = %s AND Cart_ID = %s AND CartItem.Product_ID = Product.Product_ID;"
                cursor.execute(sql5, (session['order_id'], session['order_id'], session['Cart_ID']))
                connection.commit()

                sql3 = "DELETE CartItem FROM CartItem WHERE Cart_ID = %s;"
                cursor.execute(sql3, session['Cart_ID'])
                connection.commit()
                flash("Thank you for your purchase. Your order is on the way")
                return redirect(url_for('index'))
            else:
                flash("Not enough money or empty cart")
    finally:
        connection.close()
    return redirect(url_for('index'))


def get_order_details():
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql0 = "SELECT * FROM Orders WHERE Orders.User_ID = %s;"
            cursor.execute(sql0, session['user_id'])
        connection.commit()
    finally:
        connection.close()
        cart_data = cursor.fetchall()
        return cart_data


@app.route("/orders")
@login_required
def orders():
    order_details = get_order_details()
    # print(order_details)
    return render_template('orders.html', order_details=order_details)


def order_product_details(cart_id):
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql0 = "SELECT OrderProduct.Price, OrderProduct.Quantity, Product.Title FROM OrderProduct, Product WHERE OrderProduct.Order_ID = %s AND OrderProduct.Product_ID = Product.Product_ID;"
            cursor.execute(sql0, cart_id)
        connection.commit()
    finally:
        connection.close()
        cart_data = cursor.fetchall()
        return cart_data


@app.route("/orderproduct")
@login_required
def order_product():
    order_id = request.args.get('order_id', None)
    data = order_product_details(order_id)
    cost = totalsum(data)
    return render_template('orderproduct.html', data=data, cost=cost)


if __name__ == '__main__':
    app.run(debug=True)
