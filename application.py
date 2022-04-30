from pickle import READONLY_BUFFER
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

database = []


@app.route("/")
def index():
	return render_template("login.html")


@app.route("/login", methods=["POST"])
def newUser():
	user = request.form.get("user")
	password = request.form.get("password")
	password_2 = request.form.get("password_2")

	if password == password_2:
		database.append({"user": user, "password": password})
		return render_template("login.html")

	return redirect("register")   # redireciona a la ruta "../register"


@app.route("/bienvenido", methods=["POST"])
def validateUser():
	user = request.form.get("user")
	password = request.form.get("password")

	for db in database:
		if db["user"] == user and db["password"]==password:
			return render_template("bienvenido.html", name=user)

	return redirect("login")



@app.route("/login")
def login():
	return render_template("login.html")


@app.route("/register")
def register():
	return render_template("register.html")


@app.route("/users")
def show_all_data():
	return render_template("users.html", db=database)