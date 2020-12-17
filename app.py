"""
Team BR2P

pip3 install -r requirements.txt

requirements.txt
 - pip freeze > requirements.txt

"""
#Import libraries
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, FloatField
from wtforms.fields.html5 import DateField

from wtforms.validators import InputRequired, Email, Length, EqualTo
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import price_recommender
import pandas as pd
df = pd.read_csv('product_cost.csv',
                 parse_dates=[
                              'acquire_date',
                              'published_date'
                 ])
df_raw = df.loc[~df.index_id.isna()].copy()
#--------------------------------------------------------------------------------------------------------------------------------------------
app = Flask(__name__) # Start of Flask App
bootstrap = Bootstrap(app) # For WTForms
app.config['SECRET_KEY'] = 'temporarykey123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Ignore Warning message
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3' # db Will show up in this directory
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:looper04@localhost/sgi_iot'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://xypdaowttfpuwg:6a5a8b6a1d31b236095a69e89b82a1bca9d436423a55590643747863febe5d3a@ec2-54-84-98-18.compute-1.amazonaws.com:5432/d34nik16h69tsc'
db = SQLAlchemy(app) # Initialize SQLAlchemy app

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Class that represents user database ==========================================================================================================
class Customers(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_email = db.Column(db.String(50))
    customer_id = db.Column(db.String(50))
    customer_name = db.Column(db.String(50))
    customer_type = db.Column(db.String(50))
    customer_produce = db.Column(db.String(50))
    customer_price = db.Column(db.Float)
    customer_kilo = db.Column(db.Float)
    customer_address = db.Column(db.String(200))
    customer_contact = db.Column(db.Float)
    customer_sale_dt = db.Column(db.Float)
    customer_delivery_dt = db.Column(db.DateTime)

"""
Initialize in Terminal with Python to make the User db above

>>> from app import db
>>> db.create_all()

"""
#Forms Format ===================================================================================================
@login_manager.user_loader
def load_user(user_id):
    return Customers.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Enter Username', validators=[InputRequired(), Length(min=4, max=80)])
    password = PasswordField('Enter Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=30)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80),
                                                    EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

class ProductsForm(FlaskForm):
    customer_email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    customer_name = StringField('Name', validators=[InputRequired(), Length(min=4, max=30)])
    customer_type = SelectField(u'Customer Type', validators=[InputRequired()], choices=[('Supplier', 'Supplier'), ('Restaurant', 'Restaurant'), ('Business', 'Business'), ('Corporation', 'Corporation')])
    customer_produce = SelectField(u'Customer Type', validators=[InputRequired()], choices=[('White Rice', 'White Rice'), ('Corn', 'Corn'), ('Carrots', 'Carrots'), ('Brown Rice', 'Brown Rice')])
    customer_price = FloatField('Sell Price', validators=[InputRequired()])
    customer_kilo = FloatField('Kilograms', validators=[InputRequired()])
    customer_address = StringField('Delivery Address', validators=[InputRequired(), Length(min=4, max=200)])
    customer_contact = FloatField('Contact Number', validators=[InputRequired()])
    customer_delivery_dt = DateField('Delivery Date', format='%m-%d-%Y', validators=[InputRequired()])

# Caller of Pages ===================================================================================================
# Connecting to www.website.com/home
@app.route("/home")
@app.route('/')
def index():
    #user = db.session.query(Customers.username)
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = Customers(username=form.username.data,
                        email=form.email.data,
                        password=hashed_password,
                        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Customers.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('profile'))
        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    return render_template('login.html', form=form)

@app.route('/newsfeed')
def newsfeed():
    """
    Newsfeed page
    """
    return render_template('newsfeed.html')

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():

    return render_template('profile.html')

@app.route('/sell', methods=['GET','POST'])
@login_required
def sell():
    form = InventoryForm()
    if form.validate_on_submit():
        record = Inventory(farm_id=form.farm_id.data,
                           type=form.type.data,
                           produce=form.produce.data,
                           buy_price=form.buy_price.data,
                           kilo=form.kilo.data,
                           buy_dt=form.buy_dt.data,
                           )
        db.session.add(record)
        db.session.commit()
        return redirect(url_for('thanks'))
    return render_template('sell.html', form=form)

@app.route('/calculator', methods=['GET','POST'])
@login_required
def calculator():
    return render_template('calculator.html')

@app.route('/estimate', methods=['GET','POST'])
@login_required
def estimate():
    if request.method == 'POST':
        try:
            product_name = request.form['product_name']
            rating = request.form['rating']
            brand = request.form['brand']
            product_cat = request.form['product_cat']
            parent_cat = request.form['parent_cat']
            size = request.form['size']
            brand = brand.lower()
            product_cat = product_cat.lower()

            pred = price_recommender.recommend_price(df_raw, product_name, rating, brand, product_cat, parent_cat, size)
            a,b, = pred
            print(a)
            print(b)

        except ValueError as e:
            print(e)
            return 'Please check the values!'
    return render_template('estimate.html',a=a,b=b)




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ================================================================================================================================================================================================
# End of Flask App
if __name__ == "__main__":
#    app.run(host='0.0.0.0')
   app.run(debug=True)
