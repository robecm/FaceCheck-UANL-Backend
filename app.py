from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from routes.blueprints import blueprints_list

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# SWAGGER CONFIGURATION
swaggerui_bp = get_swaggerui_blueprint('/api-docs', '/static/swagger.yaml')

# REGISTER BLUEPRINTS
for bp, url_prefix in blueprints_list:
    app.register_blueprint(bp, url_prefix=url_prefix)

# Start a new command prompt and run the ngrok tunnel script
# import subprocess
# subprocess.Popen(['start', 'cmd', '/k', r'static\ngrok_tunnel.bat'], shell=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
