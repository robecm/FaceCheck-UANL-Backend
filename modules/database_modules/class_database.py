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

# Database class to handle school classes data
class ClassesDatabase:
    def __init__(self, credentials_path='modules/credentials.json'):
        self.credentials = load_credentials(credentials_path)

    def register_class(self, **kwargs):
        class_fields = ["class_name", "teacher_id", "group_num", "semester"]
        optional_fields = ["class_room", "start_time", "end_time", "week_days"]
        if not all(field in kwargs for field in class_fields):
            return self.generate_response(success=False, error='All required fields must be present.', status_code=400)

        # Filter out optional fields that are not provided
        filtered_kwargs = {field: kwargs[field] for field in class_fields + optional_fields if field in kwargs}

        print("Received class data:", filtered_kwargs)  # Debugging print

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Insert the class data into the database
                columns = ', '.join(filtered_kwargs.keys())
                values = ', '.join([f'%({field})s' for field in filtered_kwargs.keys()])
                query = f"""
                    INSERT INTO classes ({columns})
                    VALUES ({values})
                    RETURNING class_id;
                """
                cur.execute(query, kwargs)
                print("Class registered successfully.") # Debugging print

                class_id = cur.fetchone()[0]
                print("Generated class ID:", class_id) # Debugging print
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=201)

            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                print(f"Error registering class: {error_message}") # Debugging print
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