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


# Database class to handle teacher data
class TeacherDatabase:
    def __init__(self, credentials_path='modules/database_modules/credentials.json'):
        self.credentials = load_db_credentials(credentials_path)

    def retrieve_teacher_classes(self, teacher_id):
        if not teacher_id:
            return self.generate_response(success=False, error='Teacher ID must be provided.', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                # Check if the teacher exists
                check_query = """
                    SELECT 1 FROM users_teachers
                    WHERE id = %s;
                """
                cur.execute(check_query, (teacher_id,))
                existing_teacher = cur.fetchone()
                if not existing_teacher:
                    return self.generate_response(success=False, error='Teacher not found.', status_code=404)

                # Retrieve the classes taught by the teacher
                query = """
                    SELECT * FROM classes
                    WHERE teacher_id = %s;
                """
                cur.execute(query, (teacher_id,))
                classes = cur.fetchall()
                cur.close()
                classes_dict = [dict(row) for row in classes]
                return self.generate_response(success=True, error=None, status_code=200, data=classes_dict)

            except psycopg2.Error as e:
                error_message = e.pgerror if e.pgerror else str(e)
                print(f"Error retrieving classes: {error_message}")
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