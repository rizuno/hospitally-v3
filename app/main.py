from flask import Flask
 
app = Flask(__name__,subdomain_matching=True)
 
@app.route("/")
def home_view():
        return "<h1>HI CJ! tessting subdomains</h1>"

@app.route("/", subdomain="static")
def static_index():
    """Flask supports static subdomains
    This is available at static.your-domain.tld"""
    return "static.your-domain.tld"