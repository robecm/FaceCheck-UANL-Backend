import psycopg2
import json
from contextlib import contextmanager


# Function to load database credentials from a JSON file
def load_credentials(path):
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


# Database class to handle user operations
class Database:
    def __init__(self, credentials_path='modules/credentials.json'):
        self.credentials = load_credentials(credentials_path)

    # Method to sign up a new user
    def student_signup(self, **kwargs):
        user_fields = ['name', 'username', 'age', 'faculty', 'matnum', 'password', 'face_img', 'email']
        if not all(field in kwargs for field in user_fields):
            return self.generate_response(success=False, error='Missing required fields', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Insert the new user
                query = """
                    INSERT INTO users_students (name, username, age, faculty, matnum, password, face_img, email)
                    VALUES (%(name)s, %(username)s, %(age)s, %(faculty)s, %(matnum)s, %(password)s, %(face_img)s, %(email)s)
                """
                cur.execute(query, kwargs)
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=201)

            except psycopg2.Error as e:
                error_message = e.pgerror
                print(f'Error registering student: {error_message}')

                # Check for duplication error
                if e.pgcode == '23505':  # Code for UNIQUE constraint violation
                    duplicate_field = None

                    # Loop through all fields to find the one that caused the error
                    for field in user_fields:
                        if field in error_message:
                            duplicate_field = field
                            break  # Exit loop when duplicate field is found

                    return self.generate_response(
                        success=False,
                        error=f'The {duplicate_field} already exists. Please choose a different value.',
                        status_code=409,
                        duplicate_field=duplicate_field
                    )

                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    # Method to sign up a new teacher
    def teacher_signup(self, **kwargs):
        user_fields = ['name', 'username', 'age', 'faculty', 'worknum', 'password', 'face_img', 'email']
        if not all(field in kwargs for field in user_fields):
            return self.generate_response(success=False, error='Missing required fields', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Insert the new user
                query = """
                    INSERT INTO users_teachers (name, username, age, faculty, worknum, password, face_img, email)
                    VALUES (%(name)s, %(username)s, %(age)s, %(faculty)s, %(worknum)s, %(password)s, %(face_img)s, %(email)s)
                """
                cur.execute(query, kwargs)
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=201)

            except psycopg2.Error as e:
                error_message = e.pgerror
                print(f'Error registering teacher: {error_message}')

                # Check for duplication error
                if e.pgcode == '23505':
                    duplicate_field = None

                    # Loop through all fields to find the one that caused the error
                    for field in user_fields:
                        if field in error_message:
                            duplicate_field = field
                            break

                    return self.generate_response(
                        success=False,
                        error=f'The {duplicate_field} already exists. Please choose a different value.',
                        status_code=409,
                        duplicate_field=duplicate_field
                    )

                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)


    # Method to get user by matriculation number
    def get_user_by_matnum(self, matnum):
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                query = """
                    SELECT password, face_img FROM users_students WHERE matnum = %s
                """
                cur.execute(query, (matnum,))
                result = cur.fetchone()
                cur.close()

                if result:
                    return self.generate_response(
                        success=True,
                        data={'password': result[0], 'face_img': result[1]},
                        status_code=200
                    )
                else:
                    return self.generate_response(success=False, error='User not found', status_code=404)

            except Exception as e:
                print(f'Error searching user: {e}')
                return self.generate_response(success=False, error=str(e), status_code=500)

    def get_user_by_worknum(self, worknum):
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                query = """
                       SELECT password, face_img FROM users_teachers WHERE worknum = %s
                   """
                cur.execute(query, (worknum,))
                result = cur.fetchone()
                cur.close()

                if result:
                    return self.generate_response(
                        success=True,
                        data={'password': result[0], 'face_img': result[1]},
                        status_code=200
                    )
                else:
                    return self.generate_response(success=False, error='User not found', status_code=404)

            except Exception as e:
                print(f'Error searching user: {e}')
                return self.generate_response(success=False, error=str(e), status_code=500)

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
