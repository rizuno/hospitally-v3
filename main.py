from flask import Flask
from flask import request
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__, subdomain_matching=True)
app.config["SERVER_NAME"] = "hospitally.online"  # production_server

app.config["MYSQL_HOST"] = "188.166.215.64"
app.config["MYSQL_USER"] = "hospitally_app"
app.config["MYSQL_PASSWORD"] = "wSbt?gXx+hcV8`.h"
app.config["MYSQL_DB"] = "hospitally"
mysql = MySQL(app)


@app.context_processor
def inject_static_host():
    return dict(
        static_host="https://shambles1812.github.io/"
    )  # empty string on development


@app.route("/")
def home2():
    return render_template("index.html")



@app.route("/", subdomain="www")
def home():
    return render_template("index.html")


@app.route("/", subdomain="<hospital_name>")
def static_index(hospital_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'SELECT * FROM hospital_portals WHERE hospital = "{hospital_name}"')
    # Fetch one record and return result
    row = cursor.fetchone()
    if row:
        return f'Welcome {row["hospital"]} hospital'
    else:
        return "It looks like your hospital isn't registered with us yet. Sign up now!"



if __name__ == "__main__":
    app.run(debug=True)
