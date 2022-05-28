#Grupo Amazon

from flask import Flask, render_template, request, redirect, url_for, flash
import json
import templates.algoritmo_simetrico_por_series as AlgAbs

import MySQLdb
myConnection = MySQLdb.connect( host="localhost", user="root", passwd="root", db="testdatabase")
myConnection.close()



app = Flask(__name__)
app.secret_key = 'super secret' # uso de alert

all_productos = [["AUDIFONOS RAZER KRAKEN KITTY",700,"audifonos"],
				["CÁMARA LOGITECH C920",399,"camara"],
				["LAPTOP HP CORE I5",2099,"laptop"],
				["IPHONE 13 PRO MAX",6699,"iphone"],
				["MICROFONO HYPERX QUADCAST",599,"microfono"]]

global user_name
user_name = ""

def get_data():
	try:
		with open("database.json", "r") as f:
			database = json.load(f)
	except:
		database = []
		with open("database.json", "w") as f:
			json.dump(database, f)

	return database


def save_data(a ,b):
	try:
		with open("database.json", "r+") as f:
			db = json.load(f)
			db.append({"user": a, "password": b, "products":[]})
			f.seek(0)
			json.dump(db, f)
	except:
		database = []
		with open("database.json", "w") as f:
			json.dump(database, f)
		save_data(a,b)

def save_product(a):
	with open("database.json", "r+") as f:
		db = json.load(f)
		for data in db:
			if data["user"] == user_name:
				data["products"].append(a)
				break				
		f.seek(0)
		json.dump(db, f)


@app.route("/")
def index():
	return render_template("login.html")


@app.route("/login", methods=["POST"])
def newUser():
	user = request.form.get("user")
	password = request.form.get("password")
	password_2 = request.form.get("password_2")

	if password == password_2 and user!= None and password!=None:
		for db in get_data():
			if db["user"] == user:
				flash("The account name alredy exist.")
				return redirect("register")
		save_data(user, AlgAbs.cifrado(password))
		return render_template("login.html")
	return redirect("register")   # redireciona a la ruta "../register"


@app.route("/bienvenido", methods=["POST"])
def validateUser():
	user = request.form.get("user")
	password = AlgAbs.cifrado(request.form.get("password"))

	for db in get_data():
		if db["user"] == user and db["password"] == password:
			global user_name
			user_name = user
			return render_template("bienvenido.html", name=user)

	return redirect("login")


@app.route("/cart", methods=["POST"])
def send_car():
	if user_name == "":
		return redirect("login")
	ob = int(request.form.get("object"))
	for data in get_data():
		if data["user"] == user_name and ob in data["products"]:
			return redirect("cart")
	save_product(ob)
	return redirect("cart")


@app.route("/login")
def login_render():
	global user_name
	user_name = ""
	return render_template("login.html")


@app.route("/register")
def register_render():
	global user_name
	user_name = ""
	return render_template("register.html")


@app.route("/pantalla_principal")
def pantalla_render():
	return render_template("pantalla_principal.html")

@app.route("/pantalla_principal/microfono")
def render_microfono():
	return render_template("microfono.html", precio=all_productos[4][1], nombre=all_productos[4][0])
@app.route("/pantalla_principal/camara")
def render_camara():
	return render_template("camara.html", precio=all_productos[1][1], nombre=all_productos[1][0])
@app.route("/pantalla_principal/audifonos")
def render_audifonos():
	return render_template("audifonos.html", precio=all_productos[0][1], nombre=all_productos[0][0])
@app.route("/pantalla_principal/iphone")
def render_iphone():
	return render_template("iphone.html", precio=all_productos[3][1], nombre=all_productos[3][0])
@app.route("/pantalla_principal/laptop")
def render_laptop():
	return render_template("laptop.html", precio=all_productos[2][1], nombre=all_productos[2][0])

@app.route("/info")
def info_render():
	return render_template("info.html")
@app.route("/forum")
def forum_render():
	return render_template("forum.html")

@app.route("/cart")
def carrito_render():
	if user_name == "":
		return redirect("login")
	productos = []
	for data in get_data():
		if data["user"] == user_name:
			for i in data["products"]:
				productos.append(all_productos[i])
	return render_template("cart.html", productos=productos)


@app.route("/users")
def show_all_data():
	return render_template("users.html", db=get_data())