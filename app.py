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

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer)
    from_customer_id = db.Column(db.Integer)
    my_item_id = db.Column(db.Integer)
    trade_item_id = db.Column(db.Integer)
    to_pay = db.Column(db.Integer)
    to_receive = db.Column(db.Integer)
    total_bill = db.Column(db.Integer)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer)
    product_name = db.Column(db.String(50))
    parent_category = db.Column(db.String(50))
    sub_category = db.Column(db.String(50))
    brand = db.Column(db.String(50))
    style = db.Column(db.String(50))
    rating = db.Column(db.String(50))
    size = db.Column(db.String(50))
    material = db.Column(db.String(50))
    retail_price = db.Column(db.String(50))
    color = db.Column(db.String(50))
    description = db.Column(db.String(220))
    price = db.Column(db.String(50))
    photo_path = db.Column(db.String(50))

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
def index():
    #user = db.session.query(Customers.username)
    return render_template('index.html')


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

    items = db.session.query(Customers.address,Products.product_name,Products.price,Products.photo_path,Products.brand,Products.id).join(Customers, Customers.id == Products.customer_id).all()
    # items = db.session.query(Products).join(Customers, Customers.id == Products.customer_id).all()
    return render_template('marketplace.html', user=current_user, items=items)

@app.route('/trade', methods=['GET','POST'])
@login_required
def trade():

    customer_id = request.form['customer_id']
    from_customer_id = request.form['from_customer_id']
    my_item_id = request.form['my_item_id']
    trade_item_id = request.form['trade_item_id']
    to_pay = request.form['to_pay']
    to_receive = request.form['to_receive']
    total_bill = request.form['total_bill']
    new_product = Trade(
        customer_id = customer_id,
        from_customer_id = from_customer_id,
        my_item_id = my_item_id,
        trade_item_id = trade_item_id,
        to_pay = to_pay,
        to_receive = to_receive,
        total_bill = total_bill,
    )
    db.session.add(new_product)
    db.session.commit()

    return redirect(url_for('profile'))

@app.route('/get_product', methods=['GET','POST'])
@login_required
def get_product():

    product_id = request.args['product_id']
    my_product_id = request.args['my_item']
    item = Products.query.filter_by(id=product_id).first()
    my_items = Products.query.filter_by(id=my_product_id).first()

    to_pay = 0
    to_receive = 0
    duties = 0
    logistics = 0
    service_fee = 0
    total_bill = 0

    if my_items:
        price_diff = int(my_items.price) - int(item.price)
        print(price_diff)

        if price_diff < 0:
            to_pay = abs(price_diff)
            total_bill = to_pay
        else:
            to_receive = price_diff
            total_bill = to_receive

    return jsonify({
        'my_product_id': my_product_id,
        'product_id': product_id,
        'product_name': my_items.product_name,
        'brand': my_items.brand,
        'description': my_items.description,
        'parent_category': my_items.parent_category,
        'sub_category': my_items.sub_category,
        'rating': my_items.rating,
        'material': my_items.material,
        'color': my_items.color,
        'size': my_items.size,
        'price': my_items.price,
        'to_pay': to_pay,
        'to_receive': to_receive,
        'duties': duties,
        'logistics': logistics,
        'service_fee': service_fee,
        'total_bill': total_bill,
    })

@app.route('/product', methods=['GET','POST'])
@login_required
def product():

    product_id = request.args['product_id']
    from_customer_id = 0
    item = Products.query.filter_by(id=product_id).first()
    my_items = Products.query.filter_by(customer_id=current_user.id)

    to_pay = 0
    to_receive = 0
    duties = 0
    logistics = 0
    service_fee = 0
    total_bill = 0

    if my_items:
        price_diff = int(my_items[0].price) - int(item.price)
        print(price_diff)

        if price_diff < 0:
            to_pay = abs(price_diff)
            total_bill = to_pay
        else:
            to_receive = price_diff
            total_bill = to_receive

    return render_template(
        'product.html', 
        user=current_user, 
        from_customer_id=from_customer_id,
        my_item_id=my_items[0].id,
        product_id = product_id,
        item=item, 
        my_items=my_items,
        to_pay=to_pay,
        to_receive=to_receive,
        duties=duties,
        logistics=logistics,
        service_fee=service_fee,
        total_bill=total_bill,
    )

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    items = Products.query.filter_by(customer_id=current_user.id)
    trade = Trade.query.filter_by(customer_id=current_user.id)
    return render_template('profile.html', user=current_user, items=items, trade=trade)

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
            style = request.form['style']
            material = request.form['material']
            retail_price = request.form['retail_price']
            color = request.form['color']
            description = request.form['description']
            price = request.form['price']
            brand = brand.lower()
            product_cat = product_cat.lower()

            uploaded_file = request.files['product_photo']
            if uploaded_file.filename != '':

                product_photo_path = os.path.join(ave_path,'profile/',uploaded_file.filename)
                uploaded_file.save(product_photo_path)
                print(product_photo_path)

                if request.form['button_name'] == "upload":
                    new_product = Products(
                        customer_id = current_user.id,
                        product_name = product_name,
                        parent_category = parent_cat,
                        sub_category = product_cat,
                        brand = brand,
                        style = style,
                        rating = rating,
                        size = size,
                        material = material,
                        retail_price = retail_price,
                        color = color,
                        description = description,
                        price = price,
                        photo_path = product_photo_path,
                    )
                    db.session.add(new_product)
                    db.session.commit()
                    return jsonify({'message': 'Upload success!!!'})

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
                    return jsonify({'message': 'Product info did not match to the image.'})

        except ValueError as e:
            return jsonify({'message': 'Please check the input!'})

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
