import os
from app.main import app

if __name__ == "__main__":
        port = int(os.environ.get("PORT", 5000))
        app.config['SERVER_NAME']="hospitally.online"
        app.run(debug=True, port=port)
	# app.url_map.default_subdomain = "www"
       