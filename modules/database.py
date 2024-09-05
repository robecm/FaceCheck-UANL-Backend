import psycopg2
import json


def load_credentials(path):
    with open(path, 'r') as file:
        return json.load(file)


class Database:
    def __init__(self, credentials_path='modules/credentials.json'):
        self.credentials = load_credentials(credentials_path)

    def db_connection(self):
        try:
            conn = psycopg2.connect(
                host=self.credentials['host'],
                port=self.credentials['port'],
                database=self.credentials['database'],
                user=self.credentials['user'],
                password=self.credentials['password']
            )
            return conn

        except psycopg2.DatabaseError as e:
            print(f'Error al conectar a la base de datos: {e}')
            return None

    def signup_user(self, **kwargs):
        conn = self.db_connection()
        if conn is None:
            return {'success': False, 'error': 'Error de conexión', 'status_code': 500}

        kwarg_fields = ['name', 'username', 'age', 'faculty', 'matriculation_num', 'password', 'face_img']
        if not all(field in kwargs for field in kwarg_fields):
            return {'success': False, 'error': 'Faltan campos requeridos', 'status_code': 400}

        try:
            cur = conn.cursor()
            query = """
                INSERT INTO users (name, username, age, faculty, matriculation_num, password, face_img)
                VALUES (%(name)s, %(username)s, %(age)s, %(faculty)s, %(matriculation_num)s, %(hashed_password)s, %(face_img)s)
            """
            kwargs['hashed_password'] = kwargs.pop('password')  # Hash password and add to kwargs

            cur.execute(query, kwargs)
            conn.commit()
            cur.close()
            conn.close()
            return {'success': True, 'error': None, 'status_code': 201}

        except psycopg2.Error as e:
            error_code = e.pgcode  # Capture PostgreSQL error code
            error_message = e.pgerror  # Capture PostgreSQL error message
            print(f'Error al insertar usuario: {error_message}')
            conn.close()
            return {'success': False, 'error': error_message, 'status_code': 500, 'error_code': error_code}

        finally:
            conn.close()

    @staticmethod
    def close_conn(conn):
        if conn:
            conn.close()
