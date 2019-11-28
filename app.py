from flask import Flask, render_template, flash, redirect, url_for, sessions, logging, request
"""import pymysql.cursors
from Models import UserForms
from Models.UserForms import RegisterForm, LoginForm
"""
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
        flash('Account created!')
        return redirect(url_for('index'))
    else:
        return render_template('register.html', form=form)
#login
@app.route('/login')
def login():
    form = LoginForm()
    return render_template(login.html, title='Login', form=form)

#category
@app.route('/category')
def category(id):
    #create cursor
    cur = mysql.connection.cursor()

    #get books
    result = cur.execute("SELECT * FROM Product WHERE Category_ID = id ")
    categories = cur.fetchall()

    return render_template('category.html', categories= categories)



if __name__ == '__main__':
    app.run(debug=True)