from flask import Flask
from routes.facecheck_route import facecheck_bp
from routes.user_signup_route import user_signup_bp
from routes.user_login_route import user_login_bp
import os

app = Flask(__name__)

# REGISTER BLUEPRINTS
app.register_blueprint(facecheck_bp, url_prefix='/api')
app.register_blueprint(user_signup_bp, url_prefix='/api')
app.register_blueprint(user_login_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', False), host='0.0.0.0', port=5000)
