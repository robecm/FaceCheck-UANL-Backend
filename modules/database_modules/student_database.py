import psycopg2
import psycopg2.extras
import json
from contextlib import contextmanager


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

    # TODO retrieve_student_data method

        # python
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
