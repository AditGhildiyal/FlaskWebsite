import os
from flask import Flask, render_template, redirect, url_for,flash, session
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from forms import trek_form , RegistrationForm , LoginForm
from flask_login import LoginManager, UserMixin, login_user,logout_user,login_required
from werkzeug.security import generate_password_hash,check_password_hash
from flask_wtf import FlaskForm
from wtforms import (StringField,RadioField,TextAreaField,IntegerField,SubmitField,PasswordField)
from wtforms.validators import DataRequired,Email,EqualTo
from wtforms import ValidationError
from flask_session import Session
from flask_restful import Api,Resource
import stripe

login_manager = LoginManager
base_dir = os.path.abspath(os.path.dirname(__file__))

login_manager = LoginManager()

app = Flask(__name__)
#Session(app)



public_key = 'pk_test_51OlWNiSB8AIPs1Ah1nPeObdMH39VNBLJSUelYrMrwvbNrzZvw1skECddq6I9ppjk7KHb0gatqSiISBytD7I2waNp00g5HdSjnZ'

api_key = '*************************'



stripe.api_key = api_key
app.app_context().push()

login_manager.init_app(app)
login_manager.login_view = 'login'


app.config["SECRET_KEY"] = "password"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(base_dir,"data.sqlite")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
Migrate(app,db)
"""
Trekking information database fields : trekname , duration , cost , trek_details , trek_type , 
"""

#app = Flask(__name__)

api = Api(app)


class trek_form(FlaskForm):
    trek_name = StringField("Enter trek name")
    trek_title = StringField("Enter title")
    trek_description = TextAreaField("trek description")
    trek_duration = IntegerField("Duration")
    trek_difficulty = RadioField("Difficulty:",choices=[('1','Easy'),('2','Moderate'),('3','Hard')])

    submit = SubmitField("Submit")

####################################
#
#          Forms
#
####################################


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired(),EqualTo('pass_confirm',message='Passwords Must match')])
    pass_confirm = PasswordField('Confirm Password',validators=[DataRequired()])
    submit = SubmitField("Register")

    def check_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Sorry, email has been registered already!")
        
    def check_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Sorry your username is taken.")




####################################
#
#          Models
#
####################################

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class trek_info(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.Text)
    trek_title = db.Column(db.Text)
    trek_description = db.Column(db.Text)
    trek_duration = db.Column(db.Integer)
    trek_difficulty = db.Column(db.Text)

    def __init__(self,trek_name,trek_title,trek_duration,description,difficulty):
        self.trek_name = trek_name
        self.trek_title = trek_title
        self.trek_duration = trek_duration
        self.trek_description = description
        self.trek_difficulty = difficulty
        
    def __repr__(self) -> str:
        return "Trek {} , title is {} , and duration is {}".format(self.trek_name,self.trek_title,self.trek_duration)
    
    def json(self):
        return {'Trek Name':self.trek_name,'Trek title':self.trek_title,'Trek duration':self.trek_duration,'Trek Description':self.trek_description,'Trek difficulty': self.trek_difficulty}


class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True, index = True)
    username = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))

    def __init__(self,email,username,password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)


db.create_all()
    
####################################
#
#          Resources
#
####################################

class trekResource(Resource):
    def get(self):
        trek = trek_info.query.all()

        return [t.json() for t in trek]
    

api.add_resource(trekResource,'/api/treks')

####################################
#
#          Views
#
####################################

#from forms import trek_form , RegistrationForm , LoginForm

@app.route("/")
def index():
    treks = trek_info.query.all()
    return render_template("index.html",treks=treks)

@app.route("/add_trek",methods=["GET","POST"])
def add_trek():
    form = trek_form()

    if form.validate_on_submit():
        name = form.trek_name.data
        title = form.trek_title.data
        duration = form.trek_duration.data
        description = form.trek_description.data
        difficulty = form.trek_difficulty.data


        trek_obj = trek_info(name,title,duration,description,difficulty)
        db.session.add(trek_obj)
        db.session.commit()

        return redirect(url_for("index"))
    
    return render_template("form.html",form=form)

@app.route("/trek_details/<id>")
def trek_details(id):
    print(id)
    trek = trek_info.query.get(id)
    print(trek)
    print("******************")
    return render_template("description.html",trek=trek)


@app.route("/login",methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user.check_password(form.password.data) and user is not None:
            login_user(user)
            flash("Logged in succesfully")

            next = request.args.get('next')

            if next == None or not next[0]=='/':
                next = url_for('index')

            return redirect(next)

    return render_template("login.html",form=form)

@app.route("/register",methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Thanks for registering")
        return redirect(url_for("welcome_user"))
    
    return render_template("register.html",form=form)

@app.route("/welcome")
@login_required
def welcome_user():
    return render_template("index.html")

@app.route("/api_information")
def api_information():
    return render_template("api.html")

@app.route('/pre_payment/<id>')
def pre_payment(id):
    #print("*******************************")
    trek = trek_info.query.get(id)
    #print(t)
    return render_template('pre_payment.html',public_key=public_key,trek=trek)

@app.route('/payment',methods=['POST'])
def payment():
    customer = stripe.Customer.create(email=request.form['stripeEmail'],source=request.form['stripeToken'])

    charge = stripe.Charge.create(customer=customer.id,amount=8000,currency='inr',description='Donation')

    return redirect(url_for('thank_you'))



#@app.route("/")


if __name__ == "__main__":
    app.run(debug=True)
