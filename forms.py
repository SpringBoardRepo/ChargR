from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import validators
from wtforms.fields.simple import PasswordField


class LoginForm(FlaskForm):

    email = StringField('Email', validators=[validators.InputRequired()])

    password = PasswordField('Password', validators=[
                             validators.InputRequired()])


class SignUpForm(FlaskForm):

    username = StringField('Username', validators=[validators.InputRequired()])

    first_name = StringField('First Name', validators=[
                             validators.InputRequired()])

    last_name = StringField('Last Name', validators=[
                            validators.InputRequired()])

    password = PasswordField('Password', validators=[
                             validators.InputRequired()])

    email = StringField('Email', validators=[validators.InputRequired()])


class FeedbackForm(FlaskForm):

    comment = StringField('Comment', validators=[validators.InputRequired()])
