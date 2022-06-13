from flask import Flask, render_template

app = Flask(__name__)


# @app.route("/")
# @app.route("/index")
# def index():
# 	return render_template("index.html")

@app.route("/", subdomain="static")
def static_index():
    """Flask supports static subdomains
    This is available at static.your-domain.tld"""
    return "static.your-domain.tld"

if __name__ == '__main__':
	# app.config['SERVER_NAME']='example.com'
	# app.url_map.default_subdomain = "www"
	app.run(debug=True)