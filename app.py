
from flask import Flask, config, redirect, render_template, flash, session, request, jsonify
from models import Comment, User, connect_db, db
import os
from secret import LOCAL_SECRET_KEY, OPEN_CHARGE_MAP_KEY, PSQL_PASS, MAP_BOX_API_KEY, PSQL_USER
from forms import SignUpForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError
import requests

app = Flask(__name__)

# OPEN_CHARGE_MAP_KEY = config('OPEN_CHARGE_MAP_KEY')
# MAP_BOX_API_KEY = config('MAP_BOX_API_KEY')
# LOCAL_SECRET_KEY = config('LOCAL_SECRET_KEY')

OPEN_CHARGE_MAP_KEY = os.environ.get('OPEN_CHARGE_MAP_KEY')
MAP_BOX_API_KEY = os.environ.get('MAP_BOX_API_KEY')
LOCAL_SECRET_KEY = os.environ.get('LOCAL_SECRET_KEY')

app.config["SECRET_KEY"] = os.environ.get('SECERT_KEY', LOCAL_SECRET_KEY)
app.config["OPEN_CHARGE_MAP_KEY"] = os.environ.get(
    'OPEN_CHARGE_MAP_KEY', OPEN_CHARGE_MAP_KEY)
app.config["MAP_BOX_API_KEY"] = os.environ.get(
    'MAP_BOX_API_KEY', MAP_BOX_API_KEY)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    'DATABASE_URL', f"postgresql://localhost/chargR?user=postgres&password=postgresql")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


API_BASE_URL = 'https://api.openchargemap.io/v3/poi/'
MAP_BOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places/"
# toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route('/')
def start():
    return redirect('/home')


@app.route('/home')
def home_page():
    return render_template('home.html')

########################### Location And Coords ######################################


def get_coords(location):
    """Get the location and return Latitude and Longitude """
    res = requests.get(
        f'{MAP_BOX_BASE_URL}{location}.json?access_token={MAP_BOX_API_KEY}')

    data = res.json()
    lat = data['features'][0]['center'][1]
    lng = data['features'][0]['center'][0]
    coords = {'lat': lat, 'lng': lng}
    return coords

# def get_results(data):
#     """turn json into python"""

#     res = json.loads(data.text)
#     return res


def get_info(coords):
    """Get the coords and return data """
    latitude = coords['lat']
    longitude = coords['lng']

    response = requests.get(f'{API_BASE_URL}', params={'key': OPEN_CHARGE_MAP_KEY,
                                                       'countrycode': 'US', 'latitude': latitude, 'longitude': longitude})

    return response.json()


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


@ app.route('/logout')
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
            form.username.errors.append('Username taken. Please pick another')
            return render_template('signup.html', form=form)

        session['username'] = new_user.username
        flash('Welcome, Successfully Created Your Account', 'success')
        return redirect('/home')

    return render_template('signup.html', form=form)

############################## Station Details ###########################


@ app.route('/station/detail/<int:id>')
def station_detail_page(id):
    response = requests.get(API_BASE_URL, params={
        'key': OPEN_CHARGE_MAP_KEY, 'countrycode': 'US', 'ID': id})
    data = response.json()
    comments = Comment.query.filter_by(station_id=id)
    return render_template('details.html', data=data, comments=comments)


############################# User Feedback ###############################

@ app.route('/station/detail/<int:station_id>/add-comment/<string:username>', methods=['GET', 'POST'])
def add_feedback(station_id, username):

    form = FeedbackForm()
    if form.validate_on_submit():

        comment = form.comment.data

        comment = Comment(comment=comment, user_name=username,
                          station_id=station_id)

        db.session.add(comment)
        db.session.commit()
        return redirect(f'/station/detail/{station_id}')
    return render_template('feedback.html', form=form)
