import flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, login_required
# from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
# from data import offers
from datetime import datetime
import database
from urllib.parse import urlparse, urljoin

app = Flask(__name__)
login_manager = LoginManager()

login_manager.init_app(app)

users = {
    "admin": generate_password_hash("admin123"),
}

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
 
class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        print('username', form.username.data)
        username = form.username.data
        password = form.password.data
        if username in users and \
            check_password_hash(users.get(username), password):
            user = User(username)
        # user should be an instance of your `User` class
            login_user(user)

            flask.flash('Logged in successfully.')

            next = flask.request.args.get('next')
            # is_safe_url should check if the url is safe for redirects.
            # See http://flask.pocoo.org/snippets/62/ for an example.
            if not is_safe_url(next):
                return flask.abort(400)

            return flask.redirect(next or flask.url_for('feed'))
    title = 'SeaYou - LogIn'
    return flask.render_template('login.html', form=form, title=title)

@app.route("/")
def main():
    title = 'SeaYou'
    return render_template('home.html', title=title)

@app.route("/signup")
def signup():
    title = 'SeaYou - SignUp'
    return render_template('signup.html', title=title)

@app.route("/feed")
@login_required
def feed():
    title = 'SeaYou - My Feed'
    users = database.get_users()
    offers = database.get_offers()
    return render_template('feed.html', title=title, offers=offers, users=users)

@app.route("/new")
@login_required
def new():
    title = 'SeaYou - New Offer'
    offers = database.get_offers()
    return render_template('new.html', title=title, offers=offers)