from flask import Flask
from routes.facecheck_route import facecheck_bp

app = Flask(__name__)

# REISTER BLUEPRINTS
app.register_blueprint(facecheck_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
