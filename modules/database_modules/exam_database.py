import psycopg2
import psycopg2.extras
import json
from contextlib import contextmanager


# Function to load database credentials from a JSON file
def load_credentials(path):
    with open(path, 'r') as f:
        return json.load(f)


# Function to connect to the database
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


# Database exams to handle exam data
class ExamsDatabase:
    def __init__(self, credentials_path='modules/database_modules/credentials.json'):
        self.credentials = load_credentials(credentials_path)

    def create_exam(self, **kwargs):
        exam_fields = ['exam_name', 'class_id']
        optional_fields = ['date', 'class_room', 'hour']
        if not all(field in kwargs for field in exam_fields):
            return self.generate_response(success=False, error='All required fields must be present', status_code=400)

        # Filter out optional fields that are not provided
        filtered_kwargs = {field: kwargs[field] for field in exam_fields + optional_fields if field in kwargs}
        print('Received exam data:', filtered_kwargs)  # Debugging print

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Insert the exam data into the database
                columns = ', '.join(filtered_kwargs.keys())
                values = ', '.join([f'%({field})s' for field in filtered_kwargs.keys()])
                query = f"""
                    INSERT INTO exams ({columns})
                    VALUES ({values})
                    RETURNING exam_id;
                """
                cur.execute(query, filtered_kwargs)
                print('Exam created successfully')  # Debugging print

                exam_id = cur.fetchone()[0]
                print('Generated exam ID:', exam_id)  # Debugging print
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=201)

            except psycopg2.DatabaseError as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                print(f'Error creating exam: {error_message}') # Debugging print
                return self.generate_response(success=False, error=error_message, status_code=500)


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