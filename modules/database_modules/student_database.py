import psycopg2
import psycopg2.extras
import json
from contextlib import contextmanager
import datetime


# Function to load database credentials from a JSON file
def load_db_credentials(path):
    with open(path, 'r') as file:
        return json.load(file)


# Context manager for database connection
@contextmanager
def db_connection(credentials):
    conn = None
    try:
        conn = psycopg2.connect(
            host=credentials['host'],
            port=credentials['port'],
            database=credentials['database'],
            user=credentials['user'],
            password=credentials['password']
        )
        yield conn
    except psycopg2.DatabaseError as e:
        print(f'Error connecting to the database: {e}')
        raise e
    finally:
        if conn:
            conn.close()


# Database class to handle student data
class StudentDatabase:
    def __init__(self, credentials_path='modules/database_modules/credentials.json'):
        self.credentials = load_db_credentials(credentials_path)

    def retrieve_student_teachers(self, student_id):
        if not student_id:
            return self.generate_response(success=False, error='Student ID must be provided', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                query = """
                    SELECT ut.name, ut.email, c.class_name
                    FROM classes_students cs
                    JOIN classes c ON cs.class_id = c.class_id
                    JOIN users_teachers ut ON c.teacher_id = ut.id
                    WHERE cs.student_id = %s;
                """
                cur.execute(query, (student_id,))
                teachers = cur.fetchall()
                cur.close()

                # Combine dictionaries with matching name and email
                combined_teachers = {}
                for teacher in teachers:
                    key = (teacher['name'], teacher['email'])
                    if key not in combined_teachers:
                        combined_teachers[key] = {
                            'name': teacher['name'],
                            'email': teacher['email'],
                            'class_name': [teacher['class_name']]
                        }
                    else:
                        combined_teachers[key]['class_name'].append(teacher['class_name'])

                teachers_list = list(combined_teachers.values())
                return self.generate_response(success=True, error=None, status_code=200, data=teachers_list)

            except psycopg2.DatabaseError as e:
                error_message = e.pgerror if e.pgerror else str(e)
                print('Error retrieving teachers:', error_message)
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    def retrieve_student_classes(self, student_id):
        if not student_id:
            return self.generate_response(success=False, error='Student ID must be provided.', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                # Check if the student exists
                check_query = """
                    SELECT 1 FROM users_students
                    WHERE id = %s;
                """
                cur.execute(check_query, (student_id,))
                existing_student = cur.fetchone()
                if not existing_student:
                    return self.generate_response(success=False, error='Student not found.', status_code=404)

                # Retrieve the classes attended by the student
                query = """
                    SELECT c.*, ut.name AS teacher_name
                    FROM classes_students cs
                    JOIN classes c ON cs.class_id = c.class_id
                    JOIN users_teachers ut ON c.teacher_id = ut.id
                    WHERE cs.student_id = %s;
                """
                cur.execute(query, (student_id,))
                classes = cur.fetchall()
                cur.close()
                classes_dict = [dict(row) for row in classes]
                return self.generate_response(success=True, error=None, status_code=200, data=classes_dict)

            except psycopg2.Error as e:
                error_message = e.pgerror if e.pgerror else str(e)
                print(f"Error retrieving classes: {error_message}")
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    def retrieve_student_exams(self, student_id):
        if not student_id:
            return self.generate_response(success=False, error='Student ID must be provided.', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                # Check if the student exists
                check_query = """
                    SELECT 1 FROM users_students
                    WHERE id = %s;
                """
                cur.execute(check_query, (student_id,))
                existing_student = cur.fetchone()
                if not existing_student:
                    return self.generate_response(success=False, error='Student not found.', status_code=404)

                # Retrieve the exams taken by the student
                query = """
                    SELECT e.*, er.score, c.class_name, ut.name AS teacher_name
                    FROM classes_students cs
                    JOIN exams e ON cs.class_id = e.class_id
                    JOIN classes c ON cs.class_id = c.class_id
                    JOIN users_teachers ut ON c.teacher_id = ut.id
                    JOIN exam_results er ON e.exam_id = er.exam_id 
                    AND cs.student_id = er.student_id
                    WHERE cs.student_id = %s;
                """
                cur.execute(query, (student_id,))
                exams = cur.fetchall()
                cur.close()
                exams_dict = [dict(row) for row in exams]

                # Convert datetime.date and datetime.time objects to strings
                for exam in exams_dict:
                    for key, value in exam.items():
                        if isinstance(value, datetime.date):
                            exam[key] = value.strftime('%Y-%m-%d')
                        elif isinstance(value, datetime.time):
                            exam[key] = value.strftime('%H:%M:%S')

                print(exams_dict)
                return self.generate_response(success=True, error=None, status_code=200, data=exams_dict)

            except psycopg2.Error as e:
                error_message = e.pgerror if e.pgerror else str(e)
                print(f"Error retrieving exams: {error_message}")
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    # Private method to generate a consistent JSON response
    @staticmethod
    def generate_response(success, error=None, status_code=200, **kwargs):
        response = {
            'success': success,
            'error': error,
            'status_code': status_code
        }
        response.update(kwargs)
        return response
