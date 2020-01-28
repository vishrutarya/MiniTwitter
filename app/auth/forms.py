from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User

# make the login form class by inheriting from the FlaskForm class
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

# make the signup form class by inheriting from the FlaskForm class
class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        # validate that the username hasn't already been used
        user_with_same_username = User.query.filter_by(username=username.data).first()
        if user_with_same_username is not None:
            raise ValidationError('This username is taken; please try a different one.')

    def validate_email(self, email):
        # validate that the email hasn't already been used
        user_with_same_email = User.query.filter_by(email=email.data).first()
        if user_with_same_email is not None:
            raise ValidationError('This email is taken; please try a different one.')

