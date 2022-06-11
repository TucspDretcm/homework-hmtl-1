# Grupo Amazon

from flask import Flask, render_template, request, redirect, url_for, flash, session
import templates.algoritmo_simetrico_por_series as AlgAbs

# https://www.geeksforgeeks.org/profile-application-using-python-flask-and-mysql/
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = "super secret"  # uso de alert


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'dbp'
  
  
mysql = MySQL(app)


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

    precio = request.form.get("precio")
    try:
        precio = float(precio)
    except:
        precio = 0.0

    imagen = request.form.get("imagen")
    descrip = request.form.get("descripcion")
    descrip = descrip.split("\n")
    descrip = "/n".join(descrip)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(f"SELECT * FROM Products WHERE producto='{producto}'")
        if cursor.fetchone():
            flash("alert javascript etc")
            return redirect("pantalla_principal")
    except:
        cursor.execute("""CREATE TABLE Products 
            (product_ID int PRIMARY KEY AUTO_INCREMENT, 
            producto VARCHAR(50), precio FLOAT,
            imagen VARCHAR(50),
            descripcion VARCHAR(250))""")

    cursor.execute(f"INSERT INTO Products (producto, precio, imagen, descripcion) VALUES ( '{producto}', '{precio}', '{imagen}', '{descrip}')")
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

@app.route("/forum", methods=["POST"])
def newComment():
    if 'loggedin' not in session:
        return redirect("login")

    comment = request.form.get("comment")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(f"INSERT INTO Comments (user_ID, comment) VALUES ( '{session['id']}', '{comment}')")    
        mysql.connection.commit()
    except:
        cursor.execute("CREATE TABLE Comments (user_ID int, comment VARCHAR(250))")
        cursor.execute(f"INSERT INTO Comments (user_ID, comment) VALUES ( '{session['id']}', '{comment}')")    
        mysql.connection.commit()

    return redirect("forum")


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
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(f"""SELECT pr.product_ID, pr.producto, pr.imagen FROM Products pr""")
        productos = cursor.fetchall()
    except:
        return render_template("pantalla_principal.html",dominio=session["username"], productos=[])

    return render_template("pantalla_principal.html", dominio=session["username"], productos=productos)


@app.route("/pantalla_principal/<int:id_p>")
def productos_info(id_p):
    if "loggedin" not in session:
        return redirect("login")

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(f"""SELECT * FROM Products WHERE product_ID={id_p}""")
        producto = cursor.fetchone()
        descrip = producto['descripcion'].split("/n")
    except:
        return render_template("productos_link.html", producto={"producto":None, "imagen":None,"precio":None, "descripcion":None}, descrip=[])

    return render_template("productos_link.html", producto=producto, descrip=descrip)


@app.route("/info")
def info_render():
    return render_template("info.html")


@app.route("/forum")
def forum_render():
    if "loggedin" not in session:
        return redirect("login")

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(f"""SELECT us.username, cm.comment 
            FROM Users us, Comments cm
            WHERE us.user_ID = cm.user_ID""")
    except:
        return render_template("forum.html",comments=[])

    return render_template("forum.html", comments=cursor.fetchall())


@app.route("/cart")
def carrito_render():
    if "loggedin" not in session:
        return redirect("login")

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute(f"""SELECT pr.product_ID, pr.producto, pr.precio, pr.imagen, cr.cantidad 
            FROM Products pr, Carrito cr
            WHERE cr.user_ID='{session['id']}' AND pr.product_ID=cr.product_ID""")
        productos = cursor.fetchall()
        total, con = 0, 0
        for p in productos:
            total += p['precio'] * p['cantidad']
            con += p['cantidad']
    except:
        return render_template("cart.html",productos=[], total=0.0, cantidad=0)

    return render_template("cart.html", productos=productos, total=float(total), cantidad=con)

@app.route("/cart/pay_cart")
def all_cart():
    if "loggedin" not in session:
        return redirect("login")

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("show tables like 'carrito'")
    if cursor.fetchall():
        cursor.execute(f"DELETE FROM Carrito WHERE user_ID='{session['id']}'")
        mysql.connection.commit()

    return redirect("../cart")

@app.route("/cart/<int:id_p>")
def delete_product_car(id_p):
    if "loggedin" not in session:
        return redirect("login")

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"DELETE FROM Carrito WHERE user_ID='{session['id']}' AND product_ID='{id_p}'")
    mysql.connection.commit()
    return redirect("../cart")


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
