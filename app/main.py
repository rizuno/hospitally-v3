from flask import Flask
 
app = Flask(__name__)
 
@app.route("/")
def home_view():
        return "<h1>HI CJ!</h1>"

@app.route("/", subdomain="static")
def static_index():
    """Flask supports static subdomains
    This is available at static.your-domain.tld"""
    return "static.your-domain.tld"