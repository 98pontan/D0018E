import pymysql
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SubmitField
from secrets import token_hex

from wtforms.validators import InputRequired, Length, Email


def get_categories():
    connection = pymysql.connect(host='localhost',
                                 user='oscar',
                                 password='hejsan123',
                                 db='BookCommerce',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "SELECT * FROM Category"
            result = cursor.execute(sql)
        connection.commit()

    finally:
        connection.close()
    categories = cursor.fetchall()
    return categories


class CreateProduct(Form):
    categories = get_categories()
    title = StringField('Title')
    price = StringField('Price')
    discount = StringField('Discount')
    units_in_stock = StringField('Units in stock')
    description = StringField('Description')
    isbn = StringField('ISBN')
    author = StringField('Author')
    publicer = StringField('Publicer')
    number_of_pages = StringField('Number of pages')
    language = StringField('Language')
    submit = SubmitField()


class CreateCategory(Form):
    name = StringField('Name')
    description = StringField('Description')
    submit = SubmitField()