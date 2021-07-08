from flask import Flask, config, redirect, render_template, flash, session
from models import User, connect_db, db
import os
from secret import SECRET_KEY
from forms import SignUpForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get('SECERT_KEY', SECRET_KEY)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    'DATABASE_URL', "postgresql://localhost/chargR?user=postgres&password=postgresql")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


@app.route('/')
def start():
    return redirect('/home')


@app.route('/home')
def home_page():
    return render_template('home.html')


######################## Login/Signup/Logout #######################

@app.route('/login', methods=['GET', 'POST'])
def login_page():

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            flash(f'Welcome back!,{user.username}', 'success')
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid usename/password']

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup_page():

    form = SignUpForm()

    if form.validate_on_submit():
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data
        email = form.email.data

        new_user = User.signup(username, password,
                               first_name, last_name, email)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form)

        session['username'] = new_user.username
        flash('Welcome, Successfully Created Your Account', 'success')
        return redirect('/home')

    return render_template('signup.html', form=form)
