from flask import request
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_from_directory,
    jsonify,
)
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import MySQLdb.cursors
import re
import random

app = Flask(__name__)

app.config["MYSQL_HOST"] = "188.166.215.64"
app.config["MYSQL_USER"] = "hospitally_app"
app.config["MYSQL_PASSWORD"] = "wSbt?gXx+hcV8`.h"
app.config["MYSQL_DB"] = "hospitally_v3"

mysql = MySQL(app)

bcrypt = Bcrypt()


def static_url(file_path):
    return "http://127.0.0.1:5000/" + file_path


app.jinja_env.globals.update(static_url=static_url)


@app.context_processor
def inject_static_host():
    return dict(static_host="")  # empty string on development


@app.route("/index")
def home():
    return render_template("index.html")


@app.route("/<hospital_name>/register")
def register(hospital_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        f'SELECT * FROM tbl_portal WHERE portal_slug = "{hospital_name}"'
    )  # change to portal id table
    row = cursor.fetchone()  # returns dictionary of the row
    print(row)
    if row:
        # return f'Welcome {row["portal_name"]} hospital'
        return render_template("portal-register.html", portal_name=row["portal_name"])
    else:
        return "It looks like your hospital isn't registered with us yet. Sign up now!"
    # return render_template("portal-register.html")


@app.route("/user-overview")
def user_overview():
    return render_template("hospital_portal/user-overview.html")


@app.route("/portal-page")
def portal_page():
    return render_template("portal-page.html")


# @app.route("/login")
# def login():
#     return render_template("login.html")

# POST METHOD LOGIN


@app.route("/login", methods=["POST", "GET"])
def login_post():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(username)
        print(password)
        cur.execute(
            "SELECT * FROM tbl_user WHERE user_username = %s",
            [
                username,
            ],
        )
        total_row = cur.rowcount
        print(total_row)

        if total_row > 0:
            data = cur.fetchone()
            rs_password = data["user_password_hash"]
            print(rs_password)
            if bcrypt.check_password_hash(rs_password, password):
                session["logged_in"] = True
                session["username"] = username
                msg = "success"
            else:
                msg = "No-data"
        else:
            msg = "No-data"
    return jsonify(msg)


@app.route("/register", methods=["POST", "GET"])
def register_post():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        pw_hash = bcrypt.generate_password_hash(password)  # reimplement later

        cur.execute("SELECT * FROM tbl_user WHERE user_username = % s", (username,))
        account = cur.fetchone()

        # assigns a random portal id
        cur.execute("SELECT portal_id FROM tbl_portal")
        portal_data = cur.fetchall()
        unique_portal_id = random.randint(1, 100)
        portal_ids = [x["portal_id"] for x in portal_data]
        while unique_portal_id in portal_ids:
            unique_portal_id = random.randint(1, 100)

        # assigns a random user id
        print(portal_ids)
        cur.execute("SELECT user_id FROM tbl_user")
        user_data = cur.fetchall()
        unique_user_id = random.randint(1, 100)
        user_ids = [x["user_id"] for x in user_data]
        while unique_user_id in user_ids:
            unique_user_id = random.randint(1, 100)

        if account:
            msg = "Account already exists !"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "Invalid email address !"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "Username must contain only characters and numbers !"
        elif not username or not password or not email:
            msg = "Please fill out the form !"
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # cursor.execute( "INSERT INTO tbl_user VALUES (% s, % s, % s, % s)",
            #     (
            #         unique_portal_id,
            #         username,
            #         pw_hash,
            #         email,
            #     ),
            # )
            cursor.execute(
                "INSERT INTO tbl_user VALUES (NULL, % s, % s, % s)",
                (
                    username,
                    pw_hash,
                    email,
                ),
            )
            mysql.connection.commit()
            # print(f"LENGTH OF HASH IS {len(pw_hash)} HERE")
            # cur.execute(
            #     "INSERT INTO tbl_portal (portal_id,portal_owner_user_id) VALUES (% s, % s,)",
            #     (unique_portal_id, unique_user_id),
            # )
            # mysql.connection.commit()
            print("SUCCESFULLY REGISTERED")
            msg = "You have successfully registered !"
        total_row = cur.rowcount
        print(total_row)
    return jsonify(msg)


if __name__ == "__main__":
    app.run()
