from flask import Flask, render_template
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from data import offers
from datetime import datetime

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "admin": generate_password_hash("admin123"),
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

@app.route("/")
def main():
    title = 'SeaYou'
    return render_template('home.html', title=title)

@app.route("/login")
@auth.login_required
def login():
    title = 'SeaYou - LogIn'
    return render_template('login.html', title=title)

@app.route("/signup")
def signup():
    title = 'SeaYou - SignUp'
    return render_template('signup.html', title=title)

@app.route("/feed")
def feed():
    title = 'SeaYou - My Feed'
    return render_template('feed.html', title=title, offers=offers)

@app.route("/new")
def new():
    title = 'SeaYou - New Offer'
    return render_template('new.html', title=title, offers=offers)