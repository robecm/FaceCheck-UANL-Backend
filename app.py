from flask import Flask
from routes.facecheck_route import facecheck_bp
from routes.user_signup_route import user_signup_bp
from routes.user_login_route import user_login_bp
from flask_swagger_ui import get_swaggerui_blueprint
import os
import subprocess

app = Flask(__name__)

# SWAGGER CONFIGURATION
# Create a Swagger UI blueprint to serve API documentation
swaggerui_bp = get_swaggerui_blueprint('/api-docs', '/static/swagger.yaml')

# REGISTER BLUEPRINTS
# Register the Swagger UI blueprint
app.register_blueprint(swaggerui_bp, url_prefix='/api-docs')
# Register the facecheck blueprint
app.register_blueprint(facecheck_bp, url_prefix='/api')
# Register the user signup blueprint
app.register_blueprint(user_signup_bp, url_prefix='/api')
# Register the user login blueprint
app.register_blueprint(user_login_bp, url_prefix='/api')

if __name__ == '__main__':
    # Start a new command prompt and run the ngrok tunnel script
    subprocess.Popen(['start', 'cmd', '/k', r'static\ngrok_tunnel.bat'], shell=True)
    # Run the Flask application with debug mode and specified host and port
    app.run(debug=os.getenv('FLASK_DEBUG', False), host='0.0.0.0', port=5000)
