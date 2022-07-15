from enum import unique
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
    send_file,
    Response
)
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import MySQLdb.cursors
import re
import random
import time
from datetime import date
from slugify import slugify
from werkzeug.utils import secure_filename
import os
import io
app = Flask(__name__)

app.config["MYSQL_HOST"] = "188.166.215.64"
app.config["MYSQL_USER"] = "hospitally_app"
app.config["MYSQL_PASSWORD"] = "wSbt?gXx+hcV8`.h"
app.config["MYSQL_DB"] = "hospitally_v3"
app.config["UPLOAD_FOLDER"] = "medical records"
app.secret_key = "super secret key"
mysql = MySQL(app)

bcrypt = Bcrypt()


def static_url(file_path):
    return "http://127.0.0.1:5000/" + file_path


app.jinja_env.globals.update(static_url=static_url)


@app.context_processor
def inject_static_host():
    return dict(static_host="")  # empty string on development


@app.route("/")
def home():
    if session.get("logged_in") and session.get("as_admin"):
        print("user is logged in")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        user_id = session.get("user_id")

        cursor.execute(
            f'SELECT * FROM tbl_portal WHERE portal_owner_user_id = "{user_id}"'
        )
        print(user_id)
        portal_row = cursor.fetchone()
        print(portal_row["portal_name"])
        if portal_row["portal_name"] is None:
            print("redirecting to portal creation")
            return redirect(url_for("portal_creation_page"))
        else:
            print("redirecting to portal page")
            cursor.execute(
                f'SELECT * FROM tbl_portal WHERE portal_owner_user_id = "{user_id}"'
            )
            portal_details = cursor.fetchone()
            portal_url = portal_details["portal_slug"] + ".hospitally.online"
            hospital_name = portal_details["portal_name"]
            cursor.execute(f'SELECT * FROM tbl_user WHERE user_id = "{user_id}"')

            # return render_template(
            #     "login_test.html", portal_url=portal_url, hospital_name=hospital_name
            # )  # check if user has already created a database/portal and redirect accordingly
            return redirect(
                url_for("portal_home", hospital_slug=portal_row["portal_slug"])
            )
    session["portal_id"] = "home"
    return render_template("index.html")


@app.route("/<hospital_slug>")
@app.route("/<hospital_slug>/")
def portal_home(hospital_slug, action=None):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'SELECT * FROM tbl_portal WHERE portal_slug = "{hospital_slug}"')
    row = cursor.fetchone()
    if ".ico" not in hospital_slug:
        print("SLUGG")
        print(hospital_slug)
        print(row)
        session["portal_id"] = row["portal_id"]
        session["hospital_name"] = row["portal_name"]
        print(session["portal_id"])

    if row:  # checks if the portal_slug is inside the db
        # if request.method == "POST": # add-feature portal log out
        #     if action == "logout":
        cursor.execute(
            f"SELECT * FROM tbl_medical_records_new WHERE portal_id = {session.get('portal_id') }"
        )
        medical_records_list = cursor.fetchall()
        medical_record_count = len(medical_records_list)
        cursor.execute(
            f"SELECT * FROM tbl_user WHERE portal_id = {session.get('portal_id') }"
        )
        staff_list = cursor.fetchall()
        staff_count = len(staff_list)
        print(medical_records_list)
        if session.get("logged_in") == True and session.get("as_admin") == True:
            # return "Redirecting to Admin Page"
            return render_template(
                "staff.html",
                hospital_slug=hospital_slug,
                medical_records=medical_records_list,
                staff_list=staff_list,
                medical_record_count=medical_record_count,
                staff_count=staff_count,
            )
        elif session.get("logged_in") == True and session.get("as_admin") == False:
            return render_template(
                "staff.html",
                hospital_slug=hospital_slug,
                medical_records=medical_records_list,
                staff_list=staff_list,
                medical_record_count=medical_record_count,
                staff_count=staff_count,
            )
        else:
            if action is None or action == "login":  # if session is not logged in
                return render_template(
                    "portal-login.html", portal_name=row["portal_name"]
                )
            elif action == "register":
                return render_template(
                    "portal-register.html", portal_name=row["portal_name"]
                )

    else:
        return "It looks like your hospital isn't registered with us yet. Sign up now!"


@app.route("/download", methods=["GET", "POST"])
def download():
    filename = request.args.get('filename')
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename,as_attachment=True)
    # return Response(file)
    # print(filename)
    # # return send_from_directory(directory=app.config["UPLOAD_FOLDER"], path=filename)
    # return redirect(send_file( path, as_attachment=True))


@app.route("/<hospital_name>/login", methods=["POST"])
def portal_login(hospital_name):
    """
    This is the main login page for the hospital portals
    """
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
            if (
                bcrypt.check_password_hash(rs_password, password)
                and account["authority"] == 1
            ):
                session["logged_in"] = True
                session["username"] = username
                session["user_id"] = account["user_id"]
                session["as_admin"] = True
                session["portal_id"] = account["portal_id"]
                session["first_name"] = account["user_first_name"]
                session["last_name"] = account["user_last_name"]

                msg = "success yes"
            elif (
                bcrypt.check_password_hash(rs_password, password)
                and account["authority"] == 0
                and account["portal_id"] == session["portal_id"]
            ):
                session["logged_in"] = True
                session["username"] = username
                session["user_id"] = account["user_id"]
                session["as_admin"] = False
                session["portal_id"] = account["portal_id"]
                session["first_name"] = account["user_first_name"]
                session["last_name"] = account["user_last_name"]
                msg = "success yes"
            else:
                msg = "No-data"
        else:
            msg = "No-data"
    return jsonify(msg)
    # return render_template("portal-register.html")


@app.route("/add-temporary-acc", methods=["POST"])
def add_portal_temp_acc():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        print("EXECUTED")
        username = request.form["username"]
        email = ""
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        role = request.form["roles"]
        pw_hash = bcrypt.generate_password_hash(password)  # reimplement later
        today = date.today()
        cur.execute("SELECT * FROM tbl_user WHERE user_username = % s", (username,))
        account = cur.fetchone()

        # assigns a random user id
        cur.execute("SELECT user_id FROM tbl_user")
        user_data = cur.fetchall()
        unique_user_id = random.randint(1, 100000)
        user_ids = [x["user_id"] for x in user_data]
        while unique_user_id in user_ids:
            unique_user_id = random.randint(1, 100000)

        if account:
            msg = "Account already exists !"
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "INSERT INTO tbl_user VALUES (% s,% s, % s, % s, % s, % s, % s, % s, %s, %s, %s, %s, %s, %s)",
                (
                    unique_user_id,
                    session.get("portal_id"),
                    username,
                    role,
                    pw_hash,
                    email,
                    today.strftime("%y-%m-%d %H:%M:%S"),
                    today.strftime("%y-%m-%d %H:%M:%S"),
                    "general_user",
                    '<img class="rounded-full" src="https://icon-library.com/images/default-user-icon/default-user-icon-13.jpg" alt="user image" />',
                    first_name,
                    last_name,
                    "",
                    "",
                ),
            )
            mysql.connection.commit()
            # print(f"LENGTH OF HASH IS {len(pw_hash)} HERE")
            print("SUCCESFULLY REGISTERED TEMPORARY ACCOUNT")
            msg = "You have successfully registered !"
        total_row = cur.rowcount
        print(total_row)
    return jsonify(msg)


@app.route("/user-overview")
def user_overview():
    return render_template("hospital_portal/user-overview.html")


@app.route("/portal-create-page")
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
        if portal_account["portal_name"] is None and session.get("as_admin") == True:
            return render_template("portal-creation-page.html")
        else:
            cur.execute(
                "SELECT * FROM tbl_portal WHERE portal_id = %s",
                [
                    session.get("portal_id"),
                ],
            )
            portal_account = cur.fetchone()
            return redirect(
                url_for("portal_home", hospital_slug=portal_account["portal_slug"])
            )  # change in production
    else:
        return "Please login first"


# @app.route("/login")
# def login():
#     return render_template("login.html")

# POST METHOD LOGIN


@app.route("/login", methods=["POST", "GET"])
def login_post():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    print("I GOT EXECUTED")
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
        print(account["user_authority"])
        if total_row > 0 and account["portal_id"] == session["portal_id"]:
            rs_password = account["user_password_hash"]
            print(rs_password)
            if (
                bcrypt.check_password_hash(rs_password, password)
                and account["user_authority"]=="admin"
            ):
                session["logged_in"] = True
                session["username"] = username
                session["user_id"] = account["user_id"]
                session["as_admin"] = True
                session["portal_id"] = account["portal_id"]
                session["first_name"] = account["user_first_name"]
                session["last_name"] = account["user_last_name"]
                session["bio"] = account["user_bio"]
                session["country"] = account["user_country"]
                session["email"] = account["user_email"]
                print("ADMIN SET")
                msg = "success yes"
            elif (
                bcrypt.check_password_hash(rs_password, password)
                and account["user_authority"]=="general_user"
            ):  
                print("-----------------------TEST")
                print(bcrypt.check_password_hash(rs_password, password))
                print(account["user_authority"]=="general_user")
                session["logged_in"] = True
                session["username"] = username
                session["user_id"] = account["user_id"]
                session["as_admin"] = False
                session["portal_id"] = account["portal_id"]
                session["first_name"] = account["user_first_name"]
                session["last_name"] = account["user_last_name"]
                session["bio"] = account["user_bio"]
                session["country"] = account["user_country"]
                session["email"] = account["user_email"]
                print("GENERAL USER SET")
                msg = "Account is not an admin"
            else:
                print("password is not correct")
        elif total_row > 0 and session["portal_id"] == "home":
            rs_password = account["user_password_hash"]
            print(rs_password)
            if (
                bcrypt.check_password_hash(rs_password, password)
                and account["user_authority"]=="admin"
            ):
                session["logged_in"] = True
                session["username"] = username
                session["user_id"] = account["user_id"]
                session["as_admin"] = True
                session["portal_id"] = account["portal_id"]
                session["first_name"] = account["user_first_name"]
                session["last_name"] = account["user_last_name"]
                session["bio"] = account["user_bio"]
                session["country"] = account["user_country"]
                session["email"] = account["user_email"]
                msg = "success yes"
            elif (
                bcrypt.check_password_hash(rs_password, password)
                and account["user_authority"]=="general_user"
            ):
                print("account is not an admin")

            else: 
                 print("wrong password")
            
               
            
        else:
            print("no-data")
            msg = "No-data"
    return jsonify(msg)


@app.route("/logout")
def logout():
    print("logging out")
    session.pop("logged_in", False)
    session.pop("id", None)
    session.pop("username", None)
    session.pop("portal_id", None)
    session.pop("as_admin", None)
    session.pop("first_name", None)
    session.pop("last_name", None)
    session.pop("bio", None)
    session.pop("country", None)
    session.pop("email", None)
    return redirect(url_for("home"))


@app.route("/register", methods=["POST", "GET"])
def register_post():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        pw_hash = bcrypt.generate_password_hash(password)  # reimplement later
        today = date.today()
        cur.execute("SELECT * FROM tbl_user WHERE user_username = % s", (username,))
        account = cur.fetchone()

        # assigns a random portal id
        cur.execute("SELECT portal_id FROM tbl_portal")
        portal_data = cur.fetchall()
        unique_portal_id = random.randint(1, 100000)
        portal_ids = [x["portal_id"] for x in portal_data]
        while unique_portal_id in portal_ids:
            unique_portal_id = random.randint(1, 100000)

        # assigns a random user id
        print(portal_ids)
        cur.execute("SELECT user_id FROM tbl_user")
        user_data = cur.fetchall()
        unique_user_id = random.randint(1, 100000)
        user_ids = [x["user_id"] for x in user_data]
        while unique_user_id in user_ids:
            unique_user_id = random.randint(1, 100000)

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
            print("HEY IM UPDATEDD")
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "INSERT INTO tbl_user VALUES (% s,% s, % s, % s, % s, % s, % s, % s, %s, %s, % s, % s, %s, %s )",
                (
                    unique_user_id,
                    unique_portal_id,
                    username,
                    "admin",
                    pw_hash,
                    email,
                    today.strftime("%y-%m-%d %H:%M:%S"),
                    today.strftime("%y-%m-%d %H:%M:%S"),
                    "admin",
                    '<img class="rounded-full" src="https://icon-library.com/images/default-user-icon/default-user-icon-13.jpg" alt="user image" />',
                    first_name,
                    last_name,
                    "",  # bio to be filled
                    "",  # country to be filled
                ),
            )
            mysql.connection.commit()
            session["logged_in"] = True
            session["username"] = username
            session["first_name"] = first_name
            session["last_name"] = last_name
            session["user_id"] = unique_user_id
            session["as_admin"] = True
            session["portal_id"] = unique_portal_id
            session["email"] = email
            # print(f"LENGTH OF HASH IS {len(pw_hash)} HERE")
            print("SUCCESFULLY REGISTERED")
            msg = "You have successfully registered !"
        total_row = cur.rowcount
        print(total_row)
    return jsonify(msg)


@app.route("/register_portal", methods=["POST", "GET"])
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


@app.route("/departments")
def departments():
    return render_template("departments.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":

        f = request.files["file"]
        patient_first_name = request.form["first_name"]
        patient_middle_name = request.form["middle_name"]
        patient_last_name = request.form["last_name"]
        filename = secure_filename(f.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        random_id = random.randint(1, 100000)
        f.seek(0)
        f.save(path)
        cur.execute(
            f"INSERT INTO tbl_medical_records_new VALUES ({random_id}, {session.get('portal_id')}, '{patient_first_name}', '{patient_middle_name}', '{patient_last_name}', '{filename}', '{path}')"
        )
        mysql.connection.commit()
        print(path)
        msg = "file upload successful"
    else:
        msg = "file upload failed"

    return jsonify(msg)


@app.route("/update-profile", methods=["GET", "POST"])
def update_profile():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    user_id = session.get("user_id")

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        bio = request.form["bio"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        country = request.form["country"]
        cur.execute(
            f"UPDATE tbl_user SET user_username = '{username}', user_email = '{email}', user_bio = '{bio}', user_first_name = '{first_name}', user_last_name = '{last_name}', user_country = '{country}'  WHERE user_id = {session.get('user_id')}"
        )
        mysql.connection.commit()
        session["username"] = username
        session["bio"] = bio
        session["first_name"] = first_name
        session["last_name"] = last_name
        session["country"] = country
        session["email"] = email
        msg = "successfully updated profile"
    else:
        msg = "file upload failed"
    return jsonify(msg)


if __name__ == "__main__":
    app.run()
