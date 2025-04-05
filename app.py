# Standard libs
from datetime import datetime
from urllib.parse import urlparse, urljoin
import os

# Third-party
import flask
from flask import Flask, abort, flash, redirect, render_template, request, url_for, jsonify
from flask_login import LoginManager, current_user, login_user, login_required, logout_user, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, IntegerField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Local
import database
from data import offers

app = Flask(__name__)
login_manager = LoginManager()

login_manager.init_app(app)

users = database.get_users()

app.secret_key = b'qwertyu1234567'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

class User():
    def __init__(self, username):
        self.username = username

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @classmethod
    def get(cls, username):
        return User(username)
 
class SignUpForm(FlaskForm): 
    first_name = StringField('First name')
    last_name = StringField('Last name')
    username = StringField('Username')
    dob = StringField('Date of birth')
    email = StringField('Email')
    password_hash = PasswordField('Password')
    bio = TextAreaField('About info')
    profile_picture = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')
    
class NewOfferForm(FlaskForm):
    port_departure = StringField("Port of Departure", validators=[DataRequired()])
    port_arrival = StringField("Port of Arrival", validators=[DataRequired()])
    date_departure = StringField("Date of Departure (YYYY-MM-DD)", validators=[DataRequired()])
    days = IntegerField("Number of Days", validators=[DataRequired()])
    pax = IntegerField("Number of Guests (PAX)", validators=[DataRequired()])
    price = IntegerField("Price (USD)", validators=[DataRequired()])
    picture = FileField("Boat Picture", validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField("Create Offer")

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route("/")
def main():
    title = 'SeaYou'
    user = current_user
    return render_template('home.html', title=title, user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        client = database.get_client_by_username(username)

        if client and check_password_hash(client['PasswordHash'], password):
            user = User(username)
            login_user(user)
            
            next = flask.request.args.get('next')
            if not next or not is_safe_url(next):
                next = flask.url_for('feed')

            flash('Logged in successfully.')
            return redirect(next)

    title = 'SeaYou - LogIn'
    user = current_user
    return flask.render_template('login.html', form=form, title=title, users=users, user=user)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        dob = form.dob.data
        email = form.email.data
        password_hash = generate_password_hash(form.password_hash.data)
        bio = form.bio.data

        profile_picture_filename = None
        if form.profile_picture.data:
            filename = secure_filename(form.profile_picture.data.filename)
            profile_picture_filename = filename
            form.profile_picture.data.save(os.path.join('static/ProfilePics', filename))

        database.create_user(first_name, last_name, username, dob, email, password_hash, bio, profile_picture_filename)
        new_user = User(username)
        login_user(new_user)
        next = flask.request.args.get('next')
        if not is_safe_url(next):
            return flask.abort(400)
        flash('Logged in successfully.')
        return redirect(next or flask.url_for('feed'))

    title = 'SeaYou - SignUp'
    user = current_user
    return render_template('signup.html', title=title, form=form, user=user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))

@app.route("/feed")
@login_required
def feed():
	title = 'SeaYou - My Feed'
	user_id = database.get_user_id(current_user.username)
	offers = database.get_offers_for_user(user_id)
	return render_template("feed.html", title=title, offers=offers, user=current_user)

@app.route("/new", methods=['GET', 'POST'])
@login_required
def new():
    form = NewOfferForm()
    title = 'SeaYou - New Offer'
    user = current_user

    if form.validate_on_submit():
        picture_filename = None
        if form.picture.data:
            filename = secure_filename(form.picture.data.filename)
            picture_filename = filename
            form.picture.data.save(os.path.join('static/OffersPics', filename))

        database.create_offer(
            user.username,
            form.port_departure.data,
            form.port_arrival.data,
            form.date_departure.data,
            form.days.data,
            form.pax.data,
            form.price.data,
            picture_filename
        )
        flash("New offer created!")
        return redirect(url_for('feed'))

    offers = database.get_offers()
    return render_template("new.html", title=title, form=form, user=user, offers=offers)

@app.route("/featured")
@login_required
def featured():
    title = 'SeaYou - Featured Offers'
    offers = database.get_offers()
    user = current_user
    return render_template('featured.html', title=title, offers=offers, user=user)

@app.route("/test")
def test():
    return render_template('test.html', users=users)

@app.route("/like/<int:offer_id>", methods=["POST"])
@login_required
def like_offer(offer_id):
    user_id = database.get_user_id(current_user.username)
    if database.user_liked_offer(user_id, offer_id):
        database.unlike_offer(user_id, offer_id)
        liked = False
    else:
        database.like_offer(user_id, offer_id)
        liked = True

    like_count = database.count_likes(offer_id)
    return jsonify({"liked": liked, "likeCount": like_count})
