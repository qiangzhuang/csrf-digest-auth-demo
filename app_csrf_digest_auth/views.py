from flask import Flask, g, request, Response, render_template, flash, redirect
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from . import app, db, models
from flask_httpauth import HTTPDigestAuth

app.config["SECRET_KEY"] = "thisissosecret"

auth = HTTPDigestAuth(scheme=None, realm=None, use_ha1_pw=False)

# Must store passwords in plaintext for HTTP digest auth
users = {
	"bob":"bob",
	"mallory":"mallory"
}

@auth.error_handler
def need_to_authenticate():
	return Response(response="Invalid/No Digest Auth header set", status=401, headers=None, mimetype=None, content_type=None, direct_passthrough=False)

@auth.get_password
def check_auth(username):
	if username in users:
		return users[username]
	return None



@app.route("/")
def index():
	return redirect("/accountsummary", code=302, Response=None)

@app.route("/accountsummary")
@auth.login_required
def summary():
	try:
		u = models.UserAccount.query.filter_by(username=auth.username()).first()
		return render_template("accountsummary.html", amount = u.amount, name =u.username)
	except:
		pass
	return Response(response="Some error happened", status=None, headers=None, mimetype=None, content_type=None, direct_passthrough=False)

@app.route("/login", methods=["POST", "GET"])
def login():
	return redirect("/accountsummary")

@app.route("/logout")
def logout():
	#destroy session
	return redirect("http://null:null@" + request.host + "/", code=302, Response=None)

@app.route("/transfer", methods=["POST"])
@auth.login_required
def transfer():
	transferto = request.form["username"]
	amount = float()
	try:
		amount = float(request.form["amount"])
		print amount
		user = models.UserAccount.query.filter_by(username=request.form["username"]).first()
		print user
		if user:
			currentuser = models.UserAccount.query.filter_by(username=auth.username()).first()
			currentuser.amount = currentuser.amount - amount
			user.amount = user.amount + amount
			db.session.commit()
		else:
			flash("User does not exist, transfer failed", category='message')
			return redirect("/accountsummary", code=302, Response=None)
	except:
		flash("transfer unsuccessful", category='message')
		return redirect("/accountsummary", code=302, Response=None)
	print transferto, amount
	flash("transfer successful to {0}: {1}".format(transferto, amount))
	return redirect("/accountsummary", code=302, Response=None)

