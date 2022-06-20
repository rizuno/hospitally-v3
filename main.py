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
import time
from datetime import date
from slugify import slugify

app = Flask(__name__, subdomain_matching=True)
app.config["SERVER_NAME"] = "hospitally.online"  # production_server

bcrypt = Bcrypt()
app.config["MYSQL_HOST"] = "188.166.215.64"
app.config["MYSQL_USER"] = "hospitally_app"
app.config["MYSQL_PASSWORD"] = "wSbt?gXx+hcV8`.h"
app.config["MYSQL_DB"] = "hospitally_v3"
app.secret_key = "super secret key"
mysql = MySQL(app)


def static_url(file_path):
    return "https://shambles1812.github.io/" + file_path


app.jinja_env.globals.update(static_url=static_url)


@app.context_processor
def inject_static_host():
    return dict(
        static_host="https://shambles1812.github.io/"
    )  # empty string on development


@app.route("/", subdomain="www")
def home():
    if session.get("logged_in"):
        print("user is logged in")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        user_id = session.get("user_id")
        cursor.execute(
            f'SELECT * FROM tbl_portal WHERE portal_owner_user_id = "{user_id}"'
        )
        portal_row = cursor.fetchone()
        print(portal_row["portal_name"])
        if portal_row["portal_name"] is None:
            return redirect(url_for("portal_creation_page"))
        else:
            cursor.execute(
                f'SELECT * FROM tbl_portal WHERE portal_owner_user_id = "{user_id}"'
            )
            portal_details = cursor.fetchone()
            portal_url = portal_details["portal_slug"] + ".hospitally.online"
            hospital_name = portal_details["portal_name"]
            cursor.execute(f'SELECT * FROM tbl_user WHERE user_id = "{user_id}"')
            return redirect(url_for("portal_home",portal_slug =portal_details["portal_slug"] ))
    return render_template("index.html")


@app.route("/portal-create-page", subdomain="www")
def portal_creation_page():
    if session.get("username") is not None:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(
            "SELECT * FROM tbl_portal WHERE portal_owner_user_id = %s",
            [
                session.get("user_id"),
            ],
        )
        portal_account = cur.fetchone()
        if portal_account["portal_name"] is None:
            return render_template("portal-creation-page.html")
        else:
            # return "It looks like you've created your page already"
            return redirect(url_for("portal_home",portal_slug=portal_account["portal_slug"]))
    else:
        return "Please login first"


@app.route("/", subdomain="<portal_slug>")  
@app.route("/<action>", subdomain="<portal_slug>")
def portal_home(portal_slug,action=None):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        f'SELECT * FROM tbl_portal WHERE portal_slug = "{hospital_slug}"'
    ) 
    row = cursor.fetchone()  
    print(row)
    print(action)
    if row: #checks if the portal_slug is inside the db
        if session.get("logged_in")==True and session.get("as_admin")==True:
            return "Redirecting to Admin Page"
        elif session.get("logged_in")==True and session.get("as_admin")==False:
            return "Redirecting to User Page"
        else:
            if action is None or  action == "login": # if session is not logged in
                return render_template("portal-login.html", portal_name=row["portal_name"])
            elif action == "register":
                return render_template("portal-register.html", portal_name=row["portal_name"])
        
    else:
        return "It looks like your hospital isn't registered with us yet. Sign up now!"

# post endpoints


@app.route("/login", methods=["POST", "GET"], subdomain="www")
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
        account = cur.fetchone()
        total_row = cur.rowcount
        print(total_row)

        if total_row > 0:
            rs_password = account["user_password_hash"]
            print(rs_password)
            if bcrypt.check_password_hash(rs_password, password):
                session["logged_in"] = True
                session["username"] = username
                session["user_id"] = account["user_id"]
                msg = "success yes"
            else:
                msg = "No-data"
        else:
            msg = "No-data"
    return jsonify(msg)


@app.route("/logout", subdomain="www")
def logout():
    print("logging out")
    session.pop("logged_in", False)
    session.pop("id", None)
    session.pop("username", None)
    session.pop("as_admin",None)
    return redirect(url_for("home"))


@app.route("/register", methods=["POST", "GET"], subdomain="www")
def register_post():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        pw_hash = bcrypt.generate_password_hash(password)  # reimplement later
        today = date.today()
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
            print(unique_user_id)
            print(unique_portal_id)

            cur.execute(
                "INSERT INTO tbl_portal VALUES (% s,NULL,NULL, % s, '{}')",
                (unique_portal_id, unique_user_id),
            )
            mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "INSERT INTO tbl_user VALUES (% s,% s, % s, % s, % s, % s, % s, % s)",
                (
                    unique_user_id,
                    unique_portal_id,
                    username,
                    "admin",
                    pw_hash,
                    email,
                    today,
                    today,
                ),
            )
            mysql.connection.commit()
            session["logged_in"] = True
            session["username"] = username
            session["user_id"] = unique_user_id
            session["as_admin"] = True
            # print(f"LENGTH OF HASH IS {len(pw_hash)} HERE")
            print("SUCCESFULLY REGISTERED")
            msg = "You have successfully registered !"
        total_row = cur.rowcount
        print(total_row)
    return jsonify(msg)


@app.route("/register_portal", methods=["POST", "GET"], subdomain="www")
def register_portal():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == "POST":
        portal_name = request.form["portal_name"]
        user_id = session.get("user_id")
        cur.execute(
            "SELECT * FROM tbl_portal WHERE portal_owner_user_id = %s",
            [
                user_id,
            ],
        )

        total_row = cur.rowcount

        if total_row > 0:
            cur.execute(
                "UPDATE tbl_portal SET portal_slug = %s , portal_name = %s WHERE portal_owner_user_id = %s",
                [
                    slugify(portal_name),
                    portal_name,
                    user_id,
                ],
            )
            mysql.connection.commit()
            print(slugify(portal_name))
            print(portal_name)
            print(user_id)
            print("SUCCESSFUL REGISTRATION")
            msg = "SUCCESS"
        else:
            msg = "No-data"
    return jsonify(msg)


if __name__ == "__main__":
    app.run(debug=True)
