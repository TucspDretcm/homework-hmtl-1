# Grupo Amazon

from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import templates.algoritmo_simetrico_por_series as AlgAbs

# https://www.geeksforgeeks.org/profile-application-using-python-flask-and-mysql/
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = "super secret"  # uso de alert


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'TestDataBase'
  
  
mysql = MySQL(app)


all_productos = [
    ["AUDIFONOS RAZER KRAKEN KITTY", 700.0, "audifonos.jpg"],
    ["CÁMARA LOGITECH C920", 399, "camara"],
    ["LAPTOP HP CORE I5", 2099, "laptop"],
    ["IPHONE 13 PRO MAX", 6699, "iphone"],
    ["MICROFONO HYPERX QUADCAST", 599, "microfono"],
]


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def newUser():
    user = request.form.get("user")
    password = request.form.get("password")
    password_2 = request.form.get("password_2")

    if password == password_2 and user != None and password != None:

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        try:
            cursor.execute(f"SELECT * FROM Users WHERE username='{user}'")
            if cursor.fetchone():
                    flash("The account name alredy exist. call to javascript alert(...)")
                    return redirect("register")
        except:
            cursor.execute("CREATE TABLE Users (user_ID int PRIMARY KEY AUTO_INCREMENT, username VARCHAR(50), password VARCHAR(50))")
            mysql.connection.commit()

        cursor.execute('INSERT INTO Users (username, password) VALUES (% s, % s)', ( user, AlgAbs.cifrado(password) ) )
        mysql.connection.commit()
        return render_template("login.html")

    return redirect("register")  # redireciona a la ruta "../register"


@app.route("/bienvenido", methods=["POST"])
def validateUser():
    user = request.form.get("user")
    password = AlgAbs.cifrado(request.form.get("password"))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(f"SELECT * FROM Users WHERE username='{user}' AND password='{password}'")
        account = cursor.fetchone()
        if account:
            # global user_name
            # user_name = user
            session['loggedin'] = True
            session['id'] = account['user_ID']
            session['username'] = account['username']
            return render_template("bienvenido.html", name=user)
    except:
        return redirect("login")

    return redirect("login")

@app.route("/pantalla_principal", methods=["POST"])
def newProduct():
    producto = request.form.get("producto")
    precio = float(request.form.get("precio"))
    imagen = request.form.get("imagen")

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(f"SELECT * FROM Products WHERE producto='{producto}'")
        if cursor.fetchone():
            flash("alert javascript etc")
            return redirect("pantalla_principal")
    except:
        cursor.execute("CREATE TABLE Products (product_ID int PRIMARY KEY AUTO_INCREMENT, producto VARCHAR(50), precio FLOAT,imagen VARCHAR(50))")

    cursor.execute(f"INSERT INTO Products (producto, precio, imagen) VALUES ( '{producto}', '{precio}', '{imagen}')")
    mysql.connection.commit()

    return redirect("pantalla_principal")


@app.route("/cart", methods=["POST"])
def send_car():
    if 'loggedin' not in session:
        return redirect("login")

    ob = int(request.form.get("object"))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(f"SELECT * FROM Carrito WHERE user_ID='{session['id']}' AND product_ID='{ob}'")
        if cursor.fetchone():
            cursor.execute(f"UPDATE Carrito SET cantidad=cantidad+1 WHERE user_ID='{session['id']}' AND product_ID='{ob}'")
        else:
            cursor.execute(f"INSERT INTO Carrito (user_ID, product_ID, cantidad) VALUES ( '{session['id']}', '{ob}', '{1}')")    
        mysql.connection.commit()
    except:
        cursor.execute("CREATE TABLE Carrito (user_ID int, product_ID int, cantidad int)")
        cursor.execute(f"INSERT INTO Carrito (user_ID, product_ID, cantidad) VALUES ( '{session['id']}', '{ob}', '{1}')")
        mysql.connection.commit()

    return redirect("cart")


@app.route("/login")
def login_render():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return render_template("login.html")


@app.route("/register")
def register_render():
    return render_template("register.html")


@app.route("/pantalla_principal")
def pantalla_render():
    return render_template("pantalla_principal.html", dominio=session["username"])


@app.route("/pantalla_principal/microfono")
def render_microfono():
    return render_template(
        "microfono.html", precio=all_productos[4][1], nombre=all_productos[4][0]
        )


@app.route("/pantalla_principal/camara")
def render_camara():
    return render_template(
        "camara.html", precio=all_productos[1][1], nombre=all_productos[1][0]
        )


@app.route("/pantalla_principal/audifonos")
def render_audifonos():
    return render_template(
        "audifonos.html", precio=all_productos[0][1], nombre=all_productos[0][0]
        )


@app.route("/pantalla_principal/iphone")
def render_iphone():
    return render_template(
        "iphone.html", precio=all_productos[3][1], nombre=all_productos[3][0]
        )


@app.route("/pantalla_principal/laptop")
def render_laptop():
    return render_template(
        "laptop.html", precio=all_productos[2][1], nombre=all_productos[2][0]
        )


@app.route("/info")
def info_render():
    return render_template("info.html")


@app.route("/forum")
def forum_render():
    if "loggedin" not in session:
        return redirect("login")
    return render_template("forum.html")


@app.route("/cart")
def carrito_render():
    if "loggedin" not in session:
        return redirect("login")

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(f"""SELECT pr.producto, pr.precio, pr.imagen 
            FROM Products pr, Carrito cr
            WHERE cr.user_ID='{session['id']}' AND pr.product_ID=cr.product_ID""")

    except Exception as e:
        print("\n\n\n",e,"\n\n\n")
        return render_template("cart.html")

    return render_template("cart.html", productos=cursor.fetchall())


@app.route("/mysql_preview")
def show_all_data():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Users")
    A = cursor.fetchall()
    cursor.execute("SELECT * FROM Products")
    B = cursor.fetchall()
    cursor.execute("SELECT * FROM Carrito")
    C = cursor.fetchall() 

    return render_template("mysql_preview.html", A=A, B=B, C=C)
