#Grupo Amazon

from flask import Flask, render_template, request, redirect, url_for, flash
import json

app = Flask(__name__)
app.secret_key = 'super secret' # uso de alert


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
			db.append({"user": a, "password": b})
			f.seek(0)
			json.dump(db, f)
	except:
		database = []
		with open("database.json", "w") as f:
			json.dump(database, f)
		save_data(a,b)



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
		save_data(user, password)
		return render_template("login.html")
	return redirect("register")   # redireciona a la ruta "../register"


@app.route("/bienvenido", methods=["POST"])
def validateUser():
	user = request.form.get("user")
	password = request.form.get("password")

	for db in get_data():
		if db["user"] == user and db["password"]==password:
			return render_template("bienvenido.html", name=user)

	return redirect("login")



@app.route("/login")
def login_render():
	return render_template("login.html")


@app.route("/register")
def register_render():
	return render_template("register.html")


@app.route("/pantalla_principal")
def pantalla_render():
	return render_template("pantalla_principal.html")

@app.route("/pantalla_principal/microfono")
def render_microfono():
	return render_template("microfono.html")
@app.route("/pantalla_principal/camara")
def render_camara():
	return render_template("camara.html")
@app.route("/pantalla_principal/audifonos")
def render_audifonos():
	return render_template("audifonos.html")
@app.route("/pantalla_principal/iphone")
def render_iphone():
	return render_template("iphone.html")
@app.route("/pantalla_principal/laptop")
def render_laptop():
	return render_template("laptop.html")


# @app.route("/forum", methods=["POST"])
# def inicio():
# 	posts = Post.query.order_by(Post.fecha.desc()).all() 
# 	return render_template("inicio.html", posts=posts)

# def agregar():
# 	return render_template("agregar.html")

# def crear_post():
# 	titulo = request.form.get("titulo")
# 	texto = request.form.get("texto")
# 	post = Post(titulo=titulo, texto=texto)
# 	db.session.add(post)
# 	db.session.commit()
# 	return redirect("/")

# def borrar():
# 	post_id = request.form.get("post_id")
# 	post = db.session.query(Post).filter(Post.id==post_id).first()
# 	db.session.delete(post)
# 	db.session.commit()
# 	return redirect("/")

@app.route("/info")
def info_render():
	return render_template("info.html")
@app.route("/forum")
def forum_render():
	return render_template("forum.html")

@app.route("/cart")
def carrito_render():
	return render_template("cart.html")


@app.route("/users")
def show_all_data():
	return render_template("users.html", db=get_data())
