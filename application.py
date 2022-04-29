from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

database = []

@app.route("/")
def index():
	return render_template("index.html")


@app.route("/new_user", methods=["POST"])
def newUser():

	database.append({"user": request.form.get("user"), 
					"password": request.form.get("password")})

	return render_template("session.html", data=data)


@app.route("/login", methods=["POST"])
def validate_user():
	user = request.form.get("user")
	password = request.form.get("password")

	for db in database:
		if db["user"] == user and db["password"]==password:
			return redirect(url_for("pantalla_principal.html"))
			
	return redirect(url_for("login.html"))



@app.route("/show_users")
def show_all_data():
	return render_template("users.html", db=database)