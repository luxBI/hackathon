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
from flask_wtf.file import FileField, FileRequired
from wtforms import DateField, StringField, PasswordField, BooleanField, SelectField, FloatField
from wtforms.fields.html5 import DateField

from wtforms.validators import InputRequired, Email, Length, EqualTo
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

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

    contact_number = db.Column(db.String(20))


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

    first_name = StringField('Firstname', validators=[InputRequired(), Length(min=2, max=30)])
    last_name = StringField('Lastname', validators=[InputRequired(), Length(min=1, max=30)])
    middle_name = StringField('Middlename', validators=[InputRequired(), Length(min=2, max=30)])
    age = StringField('Age', validators=[InputRequired(), Length(min=2, max=30)])
    valid_id1 = FileField('Valid ID 1', validators=[FileRequired()])
    valid_id2 = FileField('Valid ID 2', validators=[FileRequired()])
    profile_picture = FileField('Profile Picture', validators=[FileRequired()])
    address = StringField('Address', validators=[InputRequired(), Length(min=2, max=30)])
    contact_number = StringField('Contact Number', validators=[InputRequired(), Length(min=2, max=30)])
    birthday = StringField('Birthday', validators=[InputRequired(), Length(min=2, max=30)])

    credit_card_number = StringField('Card Number', validators=[InputRequired(), Length(min=2, max=30)])
    credit_card_ccv = StringField('CCV', validators=[InputRequired(), Length(min=2, max=30)])
    credit_card_expire_month = StringField('Expire Month', validators=[InputRequired(), Length(min=2, max=30)])
    credit_card_expire_year = StringField('Year', validators=[InputRequired(), Length(min=2, max=30)])

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
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
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
                return redirect(url_for('dashboard'))
        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    return render_template('login.html', form=form)

@app.route('/marketplace')
def marketplace():
    """
    Marketplace page
    """
    return render_template('marketplace.html')

@app.route('/product')
def product():
    """
    Product page
    """
    return render_template('product.html')

@app.route('/newsfeed')
def newsfeed():
    """
    Newsfeed page
    """
    return render_template('newsfeed.html')

@app.route('/profile', methods=['GET','POST'])
@login_required
def dashboard():
    return render_template('profile.html')

@app.route('/basket', methods=['GET', 'POST'])
def basket():
    form = SalesForm()
    if form.validate_on_submit():
        record = Sales(customer_email=form.customer_email.data,
                       customer_name=form.customer_name.data,
                       customer_type=form.customer_type.data,
                       customer_produce=form.customer_produce.data,
                       customer_price=form.customer_price.data,
                       customer_kilo=form.customer_kilo.data,
                       customer_address=form.customer_address.data,
                       customer_contact=form.customer_contact.data,
                       customer_delivery_dt=form.customer_delivery_dt.data,
                       )
        db.session.add(record)
        db.session.commit()
        return redirect(url_for('thanks'))
    return render_template('basket.html', form=form)

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
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
    return render_template('inventory.html', form=form)


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
