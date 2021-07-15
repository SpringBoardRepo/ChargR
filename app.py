import json
from flask import Flask, redirect, render_template, flash, session, request
from models import Comment, User, connect_db, db
import os
from secret import LOCAL_SECRET_KEY, OPEN_CHARGE_MAP_KEY, MAP_KEY, PSQL_PASS
from forms import SignUpForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError
import requests

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get('SECERT_KEY', LOCAL_SECRET_KEY)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    'DATABASE_URL', f"postgresql://localhost/chargR?user=postgres&password={PSQL_PASS}")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


API_BASE_URL = 'https://api.openchargemap.io/v3/poi/'
MAP_BASE_URL = 'http://open.mapquestapi.com/geocoding/v1/'

# toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


@app.route('/')
def start():
    return redirect('/home')


@app.route('/home')
def home_page():
    return render_template('home.html')

########################### Location And Coords ######################################


def get_coords(location):
    """Get the location and return Latitude and Longitude """

    res = requests.get(f'{MAP_BASE_URL}/address',
                       params={'key': MAP_KEY, 'location': location})
    data = res.json()
    lat = data['results'][0]['locations'][0]['latLng']['lat']
    lng = data['results'][0]['locations'][0]['latLng']['lng']
    coords = {'lat': lat, 'lng': lng}
    return coords


def get_results(data):
    """turn json into python"""

    res = json.loads(data.text)
    return res


def get_info(coords):
    """Get the coords and return data """
    latitude = coords['lat']
    longitude = coords['lng']

    response = requests.get(f'{API_BASE_URL}', params={'key': OPEN_CHARGE_MAP_KEY,
                            'countrycode': 'US', 'latitude': latitude, 'longitude': longitude})

    return get_results(response)


@ app.route('/station/results')
def search_result():
    """"Show the all results """
    location = request.args['location']

    coords = get_coords(location)
    result = get_info(coords)

    return render_template('result.html', result=result)

######################## Login/Signup/Logout #######################


@ app.route('/login', methods=['GET', 'POST'])
def login_page():
    """" User Login"""
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.authenticate(email, password)
        if user:
            session['username'] = user.username
            flash(f'Welcome back!,{user.username}', 'success')
            return redirect(f'/home')
        else:
            form.email.errors = ['Invalid username/password']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """" User Logout """
    session.pop('username')
    flash('Successfully logout', 'success')
    return redirect('/home')


@ app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    """" User SignUp"""
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

############################## Station Details ###########################


@app.route('/station/detail/<int:id>')
def station_detail_page(id):
    response = requests.get(API_BASE_URL, params={
        'key': OPEN_CHARGE_MAP_KEY, 'countrycode': 'US', 'ID': id})
    data = get_results(response)
    user = User.query.all()
    return render_template('details.html', data=data, user=user)
