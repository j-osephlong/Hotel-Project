import sys
import json
import DBINTERFACE as DB
from PASSHASH import hashpass, checkpass
import ACCOUNTMANAGER as AM
import ADMIN
import AGENT
import USER
import ROOMS

from flask import Flask
from flask import request, render_template, redirect, Response, jsonify
app = Flask(__name__)
app.register_blueprint(ADMIN.admin)
app.register_blueprint(AGENT.agent)
app.register_blueprint(USER.user)
app.register_blueprint(AM.accountmanager)
app.register_blueprint(ROOMS.rooms)

#!!!
#use url params and templates for different pages
#!!!

#FOR DEBUG ONLY
#HUGE PRIVACY AND SECURITY RISK
#NOT FOR DEPLOYMENT

@app.route("/table/<table>")
def table(table):
    return str(DB.query(table)).replace("(", "<br>").replace(")", "<br>")

@app.route("/")
def servemainpage():
    return render_template("index.html")

@app.route("/listings")
def serverlistings():
    return render_template("listings.html")

@app.route("/register")
def servehome():
	return render_template("register.html")

@app.route("/login")
def servelogin():
    return render_template("login.html")

@app.route("/admin")
def serveadmin():
    return render_template("admincheck.html")

@app.route("/account")
def serveaccount():
    return render_template("account.html")

if __name__ == "__main__":
    DB.initdb();app.run(host = '0.0.0.0', port = 5000, debug=False)#192.168.2.21