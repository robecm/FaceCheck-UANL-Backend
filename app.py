from flask import Flask
from routes.facecheck_route import facecheck_bp
from routes.student_signup_route import student_signup_bp
from routes.student_login_route import student_login_bp
from routes.teacher_login_route import teacher_login_bp
from routes.teacher_signup_route import teacher_signup_bp
from flask_swagger_ui import get_swaggerui_blueprint
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
app.register_blueprint(student_signup_bp, url_prefix='/api')
# Register the teacher signup blueprint
app.register_blueprint(teacher_signup_bp, url_prefix='/api')
# Register the user login blueprint
app.register_blueprint(student_login_bp, url_prefix='/api')
# Register the teacher login blueprint
app.register_blueprint(teacher_login_bp, url_prefix='/api')

# Start a new command prompt and run the ngrok tunnel script
# subprocess.Popen(['start', 'cmd', '/k', r'static\ngrok_tunnel.bat'], shell=True)


if __name__ == '__main__':
    # Run the Flask application with debug mode and specified host and port
    app.run(debug=True, host='0.0.0.0', port=5000)
