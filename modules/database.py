import psycopg2
import json


def load_credentials(path):
    with open(path, 'r') as file:
        return json.load(file)


class Database:
    def __init__(self, credentials_path='modules/credentials.JSON'):
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
            return False

        kwarg_fields = ['name', 'username', 'age', 'faculty', 'matriculation_num', 'password', 'face_img']
        if not all(field in kwargs for field in kwarg_fields):
            return False

        try:
            cur = conn.cursor()
            query = """
                INSERT INTO users (name, username, age, faculty, matriculation_num, password, face_img)
                VALUES (%(name)s, %(username)s, %(age)s, %(faculty)s, %(matriculation_num)s, %(hashed_password)s, %(face_img)s
            """

            cur.execute(query, kwargs)
            conn.commit()
            cur.close()

            return True

        except Exception as e:
            print(f'Error al insertar usuario: {e}')
            return False

        finally:
            conn.close()

    @staticmethod
    def close_conn(conn):
        if conn:
            conn.close()

