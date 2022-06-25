# Grupo Amazon

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify#, session
import templates.algoritmo_simetrico_por_series as AlgAbs

# https://www.geeksforgeeks.org/profile-application-using-python-flask-and-mysql/
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "super secret"  # uso de alert
CORS(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'dbp'
#app.config["USE_PERMANENT_SESSION"] = True


mysql = MySQL(app)
AccountAdministration = "amaxon"

session = {}  # simulator or global variable of "Flask/session"


@app.route("/new_user", methods=["POST"])
def newUser():
    user = request.form.get("account")
    password = request.form.get("password")

    if user != None and password != None:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("show tables like 'Users'")
        if cursor.fetchall():
            cursor.execute(f"SELECT * FROM Users WHERE username='{user}'")
            if cursor.fetchone():
                    return jsonify({"success":False})
        else:
            cursor.execute("CREATE TABLE Users (user_ID int PRIMARY KEY AUTO_INCREMENT, username VARCHAR(50), password VARCHAR(50))")

        cursor.execute('INSERT INTO Users (username, password) VALUES (% s, % s)', ( user, AlgAbs.cifrado(password) ) )
        mysql.connection.commit()

    return jsonify({"success":True})



@app.route("/validate_user", methods=["POST"])
def validateUser():
    success = False
    user = request.form.get("account")
    password = AlgAbs.cifrado(request.form.get("password"))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("show tables like 'Users'")
    if cursor.fetchall():
        cursor.execute(f"SELECT * FROM Users WHERE username='{user}' AND password='{password}'")
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['user_ID']
            session['username'] = account['username']
            success = True
    return jsonify({'success':success})



@app.route("/new_product", methods=["POST"])
def newProduct():
    if 'loggedin' not in session:
        return jsonify({'success':True})
    data = {'success':False}
    producto = request.form.get("producto")
    precio = request.form.get("precio")
    try:
        precio = float(precio)
    except:
        data["msg"] = "El precio ingresado es erroneo."
        return jsonify(data)
    imagen = request.form.get("imagen")
    descrip = request.form.get("descripcion")
    descrip = descrip.split("\n")
    descrip = "/n".join(descrip)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("show tables like 'Products'")
    if cursor.fetchall():
        cursor.execute(f"SELECT * FROM Products WHERE producto='{producto}'")
        if cursor.fetchone():
            data["msg"] = "El producto ya existe en la base de datos."
            return jsonify(data)
    else:
        cursor.execute("""CREATE TABLE Products 
            (product_ID int PRIMARY KEY AUTO_INCREMENT, 
            producto VARCHAR(50), precio FLOAT,
            imagen VARCHAR(50),
            descripcion VARCHAR(250))""")

    cursor.execute(f"INSERT INTO Products (producto, precio, imagen, descripcion) VALUES ( '{producto}', '{precio}', '{imagen}', '{descrip}')")
    mysql.connection.commit()
    data["success"] = True
    return jsonify(data)



@app.route("/logout", methods=["POST"])
def login_render():
    if "loggedin" in session:
        session.pop('loggedin', None)
    if "id" in session:
        session.pop('id', None)
    if "username" in session:
        session.pop('username', None)
    return jsonify("logout ok")


@app.route("/main_load", methods=["POST"])
def pantalla_render():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    data={"success":False}
    cursor.execute("show tables like 'Products'")
    if cursor.fetchall():
        cursor.execute(f"""SELECT pr.product_ID, pr.producto, pr.imagen FROM Products pr""")
        data['products'] = cursor.fetchall()
        data['success'] = True
        data['admi'] = False
        if 'loggedin' in session:
            data['admi'] = True if session['username'] == AccountAdministration else False
    return jsonify(data)


@app.route("/main/select", methods=["POST"])
def productos_info():
    if request.form.get("action") == "select":
        session['product_select'] = int(request.form.get("product_id"))
        return jsonify("ok save id")
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        data = {}
        cursor.execute(f"""SELECT * FROM Products WHERE product_ID={session['product_select']}""")
        data['producto'] = cursor.fetchone()
        data['producto']['descripcion'] = data['producto']['descripcion'].split("/n")
    return jsonify(data)

'''
@app.route("/pantalla_principal/set/<int:id_p>", methods=["POST"])
def productos_set(id_p):
    if "loggedin" not in session:
        return redirect("../../login")

    return f"setting element with id {id_p}"

'''
@app.route("/main/del/<string:id_p>", methods=["POST"])
def productos_del(id_p):
    if 'loggedin' not in session:
        return jsonify({'success':False})
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"DELETE FROM Products WHERE product_ID='{int(id_p)}'")
    mysql.connection.commit()
    return jsonify({'success':True})


@app.route("/forum_send", methods=["POST"])
def newComment():
    if 'loggedin' not in session:
        return jsonify({'success':False})

    comment = request.form.get("comment")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("show tables like 'comments'")
    if not cursor.fetchall():
        cursor.execute("CREATE TABLE Comments (user_ID int, comment VARCHAR(250))")

    cursor.execute(f"INSERT INTO Comments (user_ID, comment) VALUES ( '{session['id']}', '{comment}')")    
    mysql.connection.commit()
    return jsonify({'success':True})


@app.route("/forum_data", methods=["POST"])
def forum_render():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    data = {'success':False}

    cursor.execute("show tables like 'comments'")
    if cursor.fetchall():
        cursor.execute(f"""SELECT us.username, cm.comment 
            FROM Users us, Comments cm
            WHERE us.user_ID = cm.user_ID""")
        data['data'] = cursor.fetchall()
        data['success'] = True

    return jsonify(data)


@app.route("/send_cart/<string:id_p>", methods=["POST"])
def send_car(id_p):
    if 'loggedin' not in session:
        return jsonify({'success':False})

    ob = int(id_p)
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
    return jsonify({'success':True})


@app.route("/cart_loader", methods=["POST"])
def cart_loader():
    data = {'action':'vacio'}
    if "loggedin" not in session:
         data['action'] = 'registrar'
         return jsonify(data)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("show tables like 'carrito'")
    carrito = cursor.fetchone()
    cursor.execute("show tables like 'products'")
    if cursor.fetchall() and carrito:
        cursor.execute(f"""SELECT pr.product_ID, pr.producto, pr.precio, pr.imagen, cr.cantidad 
            FROM Products pr, Carrito cr
            WHERE cr.user_ID='{session['id']}' AND pr.product_ID=cr.product_ID""")
        productos = cursor.fetchall()
        total, con = 0, 0
        for p in productos:
            total += p['precio'] * p['cantidad']
            con += p['cantidad']
        data['data'] = {'productos':productos, 'total':float(total), 'cantidad':con}
        data['action'] = 'carrito'
    return jsonify(data)


@app.route("/cart/pay_cart", methods=["POST"])
def all_cart():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("show tables like 'carrito'")
    if cursor.fetchall():
        cursor.execute(f"DELETE FROM Carrito WHERE user_ID='{session['id']}'")
        mysql.connection.commit()

    return jsonify("success delete")


@app.route("/cart/<string:id_p>", methods=['POST'])
def delete_product_car(id_p):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"DELETE FROM Carrito WHERE user_ID='{session['id']}' AND product_ID='{int(id_p)}'")
    mysql.connection.commit()
    return jsonify("success delete")



@app.route("/mysql_preview", methods=["POST"])
def show_all_data():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    data = {'a':False,'b':False,'c':False}

    cursor.execute("show tables like 'users'")
    if cursor.fetchall():
        cursor.execute("SELECT * FROM Users")
        data['a'] = True
        data['data_a'] = cursor.fetchall()

    cursor.execute("show tables like 'products'")
    if cursor.fetchall():
        cursor.execute("SELECT * FROM products")
        data['b'] = True
        data['data_b'] = cursor.fetchall()

    cursor.execute("show tables like 'carrito'")
    if cursor.fetchall():
        cursor.execute("SELECT * FROM carrito")
        data['c'] = True
        data['data_c'] = cursor.fetchall()

    return jsonify(data)
