from flask import Flask
from flask_cors import CORS
from routes.face_routes.verify_face_route import verify_face_bp
from routes.login_routes.student_signup_route import student_signup_bp
from routes.login_routes.student_login_route import student_login_bp
from routes.login_routes.teacher_login_route import teacher_login_bp
from routes.login_routes.teacher_signup_route import teacher_signup_bp
from routes.face_routes.check_duplicate_route import check_duplicate_bp
from routes.face_routes.check_face_route import check_face_bp
from routes.class_routes.register_class_route import register_class_bp
from routes.class_routes.retrieve_classes_route import retrieve_classes_bp
from flask_swagger_ui import get_swaggerui_blueprint
import subprocess

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# SWAGGER CONFIGURATION
# Create a Swagger UI blueprint to serve API documentation
swaggerui_bp = get_swaggerui_blueprint('/api-docs', '/static/swagger.yaml')

# REGISTER BLUEPRINTS
# Register the Swagger UI blueprint
app.register_blueprint(swaggerui_bp, url_prefix='/api-docs')
# Register the facecheck blueprint
app.register_blueprint(verify_face_bp, url_prefix='/api')
# Register the user signup blueprint
app.register_blueprint(student_signup_bp, url_prefix='/api')
# Register the teacher signup blueprint
app.register_blueprint(teacher_signup_bp, url_prefix='/api')
# Register the user login blueprint
app.register_blueprint(student_login_bp, url_prefix='/api')
# Register the teacher login blueprint
app.register_blueprint(teacher_login_bp, url_prefix='/api')
# Register the check duplicate blueprint
app.register_blueprint(check_duplicate_bp, url_prefix='/api')
# Register the check face blueprint
app.register_blueprint(check_face_bp, url_prefix='/api')
# Register the register class blueprint
app.register_blueprint(register_class_bp, url_prefix='/api')
# Register the retrieve classes blueprint
app.register_blueprint(retrieve_classes_bp, url_prefix='/api')

# Start a new command prompt and run the ngrok tunnel script
# subprocess.Popen(['start', 'cmd', '/k', r'static\ngrok_tunnel.bat'], shell=True)

if __name__ == '__main__':
    # Run the Flask application with debug mode and specified host and port
    app.run(debug=True, host='0.0.0.0', port=5000)
