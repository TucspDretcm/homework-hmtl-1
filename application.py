from pickle import READONLY_BUFFER
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

database = []

@app.route("/")
def index():
	return render_template("index.html")


@app.route("/register", methods=["POST"])
def newUser():
	database.append({"user": request.form.get("user"), 
					"password": request.form.get("password")})
	print (database)
	return render_template("login.html")


@app.route("/bienvenido", methods=["POST"])
def validate_user():
	user = request.form.get("user")
	password = request.form.get("password")

	for db in database:
		if db["user"] == user and db["password"]==password:
			#return render_template("index.html")
			print ( "Si existe 123412132" )

	return render_template("login.html")


@app.route("/login")
def mostrarlogin():
	return render_template("login.html")





@app.route("/register")
def register():
	return render_template("register.html")


@app.route("/show_users")
def show_all_data():
	return render_template("users.html", db=database)