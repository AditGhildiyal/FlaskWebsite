from flask_wtf import FlaskForm
from wtforms import (StringField,RadioField,TextAreaField,IntegerField,SubmitField,PasswordField)
from wtforms.validators import DataRequired,Email,EqualTo
from wtforms import ValidationError
from trekking_app import User

class trek_form(FlaskForm):
    trek_name = StringField("Enter trek name")
    trek_title = StringField("Enter title")
    trek_description = TextAreaField("trek description")
    trek_duration = IntegerField("Duration")
    trek_difficulty = RadioField("Difficulty:",choices=[('1','Easy'),('2','Moderate'),('3','Hard')])

    submit = SubmitField("Submit")



class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired(),EqualTo('pass_confirm',message='Passwords Must match')])
    submit = SubmitField("Register")

    def check_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Sorry, email has been registered already!")
        
    def check_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Sorry your username is taken.")
