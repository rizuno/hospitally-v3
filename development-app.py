from flask import Flask
from flask import request
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.config["MYSQL_HOST"] = "188.166.215.64"
app.config["MYSQL_USER"] = "hospitally_app"
app.config["MYSQL_PASSWORD"] = "wSbt?gXx+hcV8`.h"
app.config["MYSQL_DB"] = "hospitally"

mysql = MySQL(app)


@app.context_processor
def inject_static_host():
    return dict(static_host="")  # empty string on development


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
