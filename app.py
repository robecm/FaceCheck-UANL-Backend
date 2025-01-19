# python
from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from routes.face_routes.verify_face_route import verify_face_bp
from routes.login_routes.student_signup_route import student_signup_bp
from routes.login_routes.student_login_route import student_login_bp
from routes.login_routes.teacher_login_route import teacher_login_bp
from routes.login_routes.teacher_signup_route import teacher_signup_bp
from routes.login_routes.check_duplicate_route import check_duplicate_bp
from routes.face_routes.check_face_route import check_face_bp
from routes.class_routes.register_class_route import register_class_bp
from routes.class_routes.retrieve_teacher_classes_route import retrieve_teacher_classes_bp
from routes.class_routes.update_class_route import update_class_bp
from routes.class_routes.delete_class_route import delete_class_bp
from routes.class_routes.student_class_route import student_class_bp
from routes.class_routes.retrieve_class_students_route import retrieve_class_students_bp
from routes.class_routes.delete_student_class import delete_student_class_bp
from routes.exam_routes.create_exam_route import create_exam_bp
from routes.exam_routes.update_exam_route import update_exam_bp
from routes.exam_routes.delete_exam_route import delete_exam_bp
from routes.class_routes.retrieve_class_exams_route import retrieve_class_exams_bp
from routes.exam_routes.add_exam_result import add_exam_result_bp
from routes.exam_routes.update_exam_result_route import update_exam_result_bp
from routes.exam_routes.retrieve_exam_results_route import retrieve_exam_results_bp
from routes.exam_routes.delete_exam_result import delete_exam_result_bp
from routes.class_routes.retrieve_student_classes_route import retrieve_student_classes_bp
from routes.student_routes.retrieve_student_teachers_route import retrieve_student_teachers_bp

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# SWAGGER CONFIGURATION
swaggerui_bp = get_swaggerui_blueprint('/api-docs', '/static/swagger.yaml')

# REGISTER BLUEPRINTS
blueprints = [
    (swaggerui_bp, '/api-docs'),
    (verify_face_bp, '/api'),
    (student_signup_bp, '/api'),
    (teacher_signup_bp, '/api'),
    (student_login_bp, '/api'),
    (teacher_login_bp, '/api'),
    (check_duplicate_bp, '/api'),
    (check_face_bp, '/api'),
    (register_class_bp, '/api'),
    (retrieve_teacher_classes_bp, '/api'),
    (update_class_bp, '/api'),
    (delete_class_bp, '/api'),
    (student_class_bp, '/api'),
    (retrieve_class_students_bp, '/api'),
    (delete_student_class_bp, '/api'),
    (create_exam_bp, '/api'),
    (update_exam_bp, '/api'),
    (delete_exam_bp, '/api'),
    (retrieve_class_exams_bp, '/api'),
    (add_exam_result_bp, '/api'),
    (update_exam_result_bp, '/api'),
    (retrieve_exam_results_bp, '/api'),
    (delete_exam_result_bp, '/api'),
    (retrieve_student_classes_bp, '/api'),
    (retrieve_student_teachers_bp, '/api')
]

for bp, url_prefix in blueprints:
    app.register_blueprint(bp, url_prefix=url_prefix)

# Start a new command prompt and run the ngrok tunnel script
# subprocess.Popen(['start', 'cmd', '/k', r'static\ngrok_tunnel.bat'], shell=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)