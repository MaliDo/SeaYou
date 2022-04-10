from flask import Flask, render_template
from data import offers
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def main():
    title = 'SeaYou'
    return render_template('home.html', title=title)

@app.route("/login")
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