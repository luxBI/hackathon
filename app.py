"""
Team BR2P

pip3 install -r requirements.txt

requirements.txt
 - pip freeze > requirements.txt

"""
#Import libraries
from flask import session, Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, FloatField
from wtforms.fields.html5 import DateField

from wtforms.validators import InputRequired, Email, Length, EqualTo
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.file import FileField, FileRequired

import os.path
ave_path = 'static/'
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from flask_wtf.file import FileField

import pickle
import vectorize_image_ver2
import joblib

import price_recommender
import pandas as pd
df_XY = pd.read_csv('df_XY.csv').drop('Unnamed: 0', axis=1)
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

    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    middle_name = db.Column(db.String(20))
    age = db.Column(db.String(20))
    address = db.Column(db.String(20))
    contact_number = db.Column(db.String(20))
    birthday = db.Column(db.String(20))
    credit_card_number = db.Column(db.String(20))
    credit_card_ccv = db.Column(db.String(20))
    credit_card_expire_month = db.Column(db.String(20))
    credit_card_expire_year = db.Column(db.String(20))

    profile_picture = db.Column(db.String(40))
    valid_id1 = db.Column(db.String(40))
    valid_id2 = db.Column(db.String(40))

    #contact_number = db.Column(db.String(20))

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
    password = PasswordField('Enter Password', validators=[InputRequired(), Length(min=3, max=80)])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=3, max=11)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=3, max=11),
                                                    EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

    first_name = StringField('Firstname')
    last_name = StringField('Lastname')
    middle_name = StringField('Middlename')
    age = StringField('Age')
    valid_id1 = FileField('Valid ID 1')
    valid_id2 = FileField('Valid ID 2')
    profile_picture = FileField('Profile Picture')
    address = StringField('Address')
    contact_number = StringField('Contact Number')
    birthday = StringField('Birthday')

    credit_card_number = StringField('Card Number')
    credit_card_ccv = StringField('CCV')
    credit_card_expire_month = StringField('Expire Month')
    credit_card_expire_year = StringField('Year')

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
@login_required
def index():
    #user = db.session.query(Customers.username)
    return render_template('index.html', user=current_user)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():

        profile_picture_path = ""
        valid_id1_path = ""
        valid_id2_path = ""
        
        uploaded_file = request.files['profile_picture']
        if uploaded_file.filename != '':

            profile_picture_path = os.path.join(ave_path,'profile/',uploaded_file.filename)
            uploaded_file.save(profile_picture_path)
            print(profile_picture_path)

        uploaded_file = request.files['valid_id1']
        if uploaded_file.filename != '':

            valid_id1_path = os.path.join(ave_path,'profile/',uploaded_file.filename)
            uploaded_file.save(valid_id1_path)
            print(valid_id1_path)
            # vectorize = vectorize_image_ver2.vectorize_image(input)
            # print(vectorize)

        uploaded_file = request.files['valid_id2']
        if uploaded_file.filename != '':

            valid_id2_path = os.path.join(ave_path,'profile/',uploaded_file.filename)
            uploaded_file.save(valid_id2_path)
            print(valid_id2_path)
            # vectorize = vectorize_image_ver2.vectorize_image(input)
            # print(vectorize)
            
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = Customers(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            middle_name=form.middle_name.data,
            age=form.age.data,
            address=form.address.data,
            contact_number=form.contact_number.data,
            birthday=form.birthday.data,
            credit_card_number=form.credit_card_number.data,
            credit_card_ccv=form.credit_card_ccv.data,
            credit_card_expire_month=form.credit_card_expire_month.data,
            credit_card_expire_year=form.credit_card_expire_year.data,
            password=hashed_password,
            profile_picture=profile_picture_path,
            valid_id1=valid_id1_path,
            valid_id2=valid_id2_path,

        )
        db.session.add(new_user)
        db.session.commit()
            
        # session['user'] = new_user
        return redirect(url_for('profile'))
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
@login_required
def newsfeed():
    """
    Newsfeed page
    """
    return render_template('newsfeed.html', user=current_user)

@app.route('/marketplace')
@login_required
def marketplace():
    """
    Marketplace page
    """
    return render_template('marketplace.html', user=current_user)

@app.route('/product')
@login_required
def product():
    """
    Product page
    """
    return render_template('product.html', user=current_user)

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    return render_template('profile.html', user=current_user)

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
# @login_required
def calculator():
    return render_template('calculator.html')

@app.route('/add_item', methods=['GET','POST'])
# @login_required
def add_item():

    a = 0
    b = 0
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

            uploaded_file = request.files['product_photo']
            if uploaded_file.filename != '':

                product_photo_path = os.path.join(ave_path,'profile/',uploaded_file.filename)
                uploaded_file.save(product_photo_path)
                print(product_photo_path)

                vectorize = vectorize_image_ver2.vectorize_image(product_photo_path)
                print(vectorize)
                file_ = open('adagbm_parent_cat_ver3.joblib', 'rb')
                loaded_model = joblib.load(file_)
                category_output = loaded_model.predict(vectorize)
                print(category_output)

                model_product_cat_back  = pickle.load(open('static/models/sub_category/model_product_cat_backpack.pickle', 'rb'))
                is_back = model_product_cat_back.predict(vectorize)[0]

                model_product_cat_travel  = pickle.load(open('static/models/sub_category/model_product_cat_travel bag.pickle', 'rb'))
                is_travel = model_product_cat_travel.predict(vectorize)[0]

                model_product_cat_tote  = pickle.load(open('static/models/sub_category/model_product_cat_tote bag.pickle', 'rb'))
                is_tote = model_product_cat_tote.predict(vectorize)[0]

                model_product_cat_shoulder  = pickle.load(open('static/models/sub_category/model_product_cat_shoulder bag.pickle', 'rb'))
                is_shoulder = model_product_cat_shoulder.predict(vectorize)[0]

                model_product_cat_satchel  = pickle.load(open('static/models/sub_category/model_product_cat_satchel.pickle', 'rb'))
                is_satchel = model_product_cat_satchel.predict(vectorize)[0]

                model_product_cat_hobo  = pickle.load(open('static/models/sub_category/model_product_cat_hobo bag.pickle', 'rb'))
                is_hobo = model_product_cat_hobo.predict(vectorize)[0]

                model_product_cat_handbag  = pickle.load(open('static/models/sub_category/model_product_cat_handbag.pickle', 'rb'))
                is_hand = model_product_cat_handbag.predict(vectorize)[0]

                model_product_cat_clutch  = pickle.load(open('static/models/sub_category/model_product_cat_clutch bag.pickle', 'rb'))
                is_clutch = model_product_cat_clutch.predict(vectorize)[0]

                model_product_cat_business  = pickle.load(open('static/models/sub_category/model_product_cat_business bag.pickle', 'rb'))
                is_business = model_product_cat_business.predict(vectorize)[0]

                model_product_cat_bucket  = pickle.load(open('static/models/sub_category/model_product_cat_bucket bag.pickle', 'rb'))
                is_bucket = model_product_cat_bucket.predict(vectorize)[0]

                model_product_cat_boston  = pickle.load(open('static/models/sub_category/model_product_cat_boston bag.pickle', 'rb'))
                is_boston = model_product_cat_boston.predict(vectorize)[0]

                model_product_cat_belt  = pickle.load(open('static/models/sub_category/model_product_cat_belt bag.pickle', 'rb'))
                is_belt = model_product_cat_belt.predict(vectorize)[0]

                # 1 - slg
                # 0 - bag
                dummy = {'slg': 1, 'bag':0}
                dummy_cat = {
                'travel_bag': is_travel,
                'tote_bag': is_tote,
                'shoulder_bag': is_shoulder,
                'satchel': is_satchel,
                'hobo_bag': is_hobo,
                'handbag': is_hand,
                'clutch': is_clutch,
                'business_bag': is_business,
                'boston_bag': is_boston,
                'belt_bag': is_belt,
                'backpack': is_back
                }

                model_checker = 1
                result_parent_cat = "bag" if category_output[0] == 0 else "slg"
                if result_parent_cat == parent_cat:
                    if dummy_cat[product_cat]:
                        print('hello world')
                        print(product_name, rating, brand, product_cat, parent_cat, size)
                        pred = price_recommender.recommend_price(df_XY, product_name, rating, brand, ' '.join(product_cat.split('_')), parent_cat, size)
                        a,b, = pred
                    else:
                        model_checker = 0
                else:
                    model_checker = 0

                if not model_checker:
                    return jsonify({'message': 'Please check product image!'})

        except ValueError as e:
            return jsonify({'message': 'Please check the values!'})
    return jsonify({'a': a, 'b': b, 'message': ""})




@app.route('/logout')
@login_required
def logout():
    logout_user()
    # session.pop('user', None)
    return redirect(url_for('index'))

# ================================================================================================================================================================================================
# End of Flask App
if __name__ == "__main__":
#    app.run(host='0.0.0.0')
   app.run(debug=True)
