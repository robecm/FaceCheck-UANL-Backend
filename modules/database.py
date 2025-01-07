import psycopg2
import json
import base64
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

    # Method to sign up a new student (split image storage)
    def student_signup(self, **kwargs):
        user_fields = ['name', 'username', 'age', 'faculty', 'matnum', 'password', 'email']
        if not all(field in kwargs for field in user_fields):
            return self.generate_response(success=False, error='Missing required fields', status_code=400)

        face_img = kwargs.pop('face_img', None)
        print("Student signup data:", kwargs)  # Debugging print

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Insert the new user without face_img
                query = """
                    INSERT INTO users_students (name, username, age, faculty, matnum, password, email)
                    VALUES (%(name)s, %(username)s, %(age)s, %(faculty)s, %(matnum)s, %(password)s, %(email)s)
                    RETURNING id;
                """
                cur.execute(query, kwargs)
                print("Student inserted")  # Debugging print

                student_id = cur.fetchone()[0]
                print("Inserted student ID:", student_id)  # Debugging print

                # Insert face image in separate table
                print("Face image:", face_img)  # Debugging print
                if face_img:
                    print("Inserting face image")  # Debugging print
                    face_query = """
                        INSERT INTO faces_students (student_id, face_img) VALUES (%s, %s) RETURNING face_id;
                    """
                    cur.execute(face_query, (student_id, face_img))
                    print("Face image inserted")  # Debugging print
                    face_id = cur.fetchone()[0]
                    print("Inserted face ID:", face_id)  # Debugging print

                    # Update student record with face_id
                    update_query = """
                        UPDATE users_students SET face_id = %s WHERE id = %s;
                    """
                    print("Updating student record")  # Debugging print
                    cur.execute(update_query, (face_id, student_id))

                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=201)

            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror
                print(f'Error registering student: {error_message}')  # Debugging print

                if e.pgcode == '23505':
                    duplicate_field = next((field for field in user_fields if field in error_message), None)
                    return self.generate_response(
                        success=False,
                        error=f'The {duplicate_field} already exists. Please choose a different value.',
                        status_code=409,
                        duplicate_field=duplicate_field
                    )

                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    # Method to sign up a new teacher
    def teacher_signup(self, **kwargs):
        user_fields = ['name', 'username', 'age', 'faculty', 'worknum', 'password', 'email']
        if not all(field in kwargs for field in user_fields):
            return self.generate_response(success=False, error='Missing required fields', status_code=400)

        face_img = kwargs.pop('face_img', None)
        print("Teacher signup data:", kwargs)  # Debugging print

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Insert the new teacher without face_img
                query = """
                    INSERT INTO users_teachers (name, username, age, faculty, worknum, password, email)
                    VALUES (%(name)s, %(username)s, %(age)s, %(faculty)s, %(worknum)s, %(password)s, %(email)s)
                    RETURNING id;
                """
                cur.execute(query, kwargs)
                teacher_id = cur.fetchone()[0]
                print("Inserted teacher ID:", teacher_id)  # Debugging print

                # Insert face image in separate table
                if face_img:
                    face_query = """
                        INSERT INTO teacher_faces (teacher_id, face_img) VALUES (%s, %s) RETURNING face_id;
                    """
                    cur.execute(face_query, (teacher_id, face_img))
                    face_id = cur.fetchone()[0]
                    print("Inserted face ID:", face_id)  # Debugging print

                    update_query = """
                        UPDATE users_teachers SET face_id = %s WHERE id = %s;
                    """
                    cur.execute(update_query, (face_id, teacher_id))

                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=201)

            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror
                print(f'Error registering teacher: {error_message}')  # Debugging print

                if e.pgcode == '23505':
                    duplicate_field = next((field for field in user_fields if field in error_message), None)
                    return self.generate_response(
                        success=False,
                        error=f'The {duplicate_field} already exists. Please choose a different value.',
                        status_code=409,
                        duplicate_field=duplicate_field
                    )

                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    # Method to get user by matriculation number
    def get_user_by_matnum(self, matnum):
        print("Searching user by matnum:", matnum)  # Debugging print
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                query = """
                    SELECT u.password, f.face_img
                    FROM users_students u
                    LEFT JOIN faces_students f ON u.id = f.student_id
                    WHERE u.matnum = %s
                """
                cur.execute(query, (matnum,))
                result = cur.fetchone()
                cur.close()

                if result:
                    print("User found:", result)  # Debugging print
                    password = result[0]
                    face_img_memoryview = result[1]
                    print("Face image:", face_img_memoryview[:100])  # Debugging print
                    face_img_base64 = base64.b64encode(face_img_memoryview).decode('utf-8')
                    print("Face image base64:", face_img_base64[:100])  # Debugging print
                    face_img_decoded = base64.b64decode(face_img_base64)
                    print("Face image decoded:", face_img_decoded[:100])  # Debugging print
                    return self.generate_response(
                        success=True,
                        data={'password': password, 'face_img': face_img_decoded},
                        status_code=200
                    )
                else:
                    print("User not found")  # Debugging print
                    return self.generate_response(success=False, error='User not found', status_code=404)

            except Exception as e:
                print(f'Error searching user: {e}')  # Debugging print
                return self.generate_response(success=False, error=str(e), status_code=500)

    def get_user_by_worknum(self, worknum):
        print("Searching user by worknum:", worknum)  # Debugging print
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
                    print("User found:", result)  # Debugging print
                    return self.generate_response(
                        success=True,
                        data={'password': result[0], 'face_img': result[1]},
                        status_code=200
                    )
                else:
                    print("User not found")  # Debugging print
                    return self.generate_response(success=False, error='User not found', status_code=404)

            except Exception as e:
                print(f'Error searching user: {e}')  # Debugging print
                return self.generate_response(success=False, error=str(e), status_code=500)

    # Method to check if a user already exists based on email, matnum, or username
    def check_user_exists(self, email, matnum, username):
        print("Checking if user exists with email, matnum, or username")  # Debugging print
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                query = """
                    SELECT 'email' AS field FROM users_students WHERE email = %s
                    UNION
                    SELECT 'matnum' AS field FROM users_students WHERE matnum = %s
                    UNION
                    SELECT 'username' AS field FROM users_students WHERE username = %s
                    UNION
                    SELECT 'email' AS field FROM users_teachers WHERE email = %s
                    UNION
                    SELECT 'worknum' AS field FROM users_teachers WHERE worknum = %s
                    UNION
                    SELECT 'username' AS field FROM users_teachers WHERE username = %s
                """
                cur.execute(query, (email, matnum, username, email, matnum, username))
                result = cur.fetchone()
                cur.close()

                if result:
                    print("User already exists:", result)  # Debugging print
                    return self.generate_response(success=False, error='User already exists', status_code=409, duplicate_field=result[0])
                else:
                    print("User does not exist")  # Debugging print
                    return self.generate_response(success=True, error=None, status_code=200)

            except Exception as e:
                print(f'Error checking user existence: {e}')  # Debugging print
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