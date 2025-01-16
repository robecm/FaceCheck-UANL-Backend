import psycopg2
import psycopg2.extras
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

    def retrieve_classes(self, teacher_id):
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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

    def update_class(self, class_id, **kwargs):
        class_fields = ["class_name", "teacher_id", "group_num", "semester"]
        optional_fields = ["class_room", "start_time", "end_time", "week_days"]

        if not class_id:
            return self.generate_response(success=False, error='Class ID must be provided.', status_code=400)

        # Filter out optional fields that are not provided
        filtered_kwargs = {field: kwargs[field] for field in class_fields + optional_fields if field in kwargs}

        if not filtered_kwargs:
            return self.generate_response(success=False, error='No fields to update.', status_code=400)
        print('Received data:', filtered_kwargs)  # Debugging print

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Construct the query dynamically
                set_clause = ', '.join([f'{field} = %({field})s' for field in filtered_kwargs.keys()])
                query = f"""
                    UPDATE classes
                    SET {set_clause}
                    WHERE class_id = %(class_id)s
                    RETURNING class_id;
                """
                filtered_kwargs['class_id'] = class_id
                cur.execute(query, filtered_kwargs)
                print("Class updated successfully.")  # Debugging print

                updated_class_id = cur.fetchone()[0]
                print("Updated class ID:", updated_class_id)  # Debugging print
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=200, data={'class_id': updated_class_id})

            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                print(f"Error updating class: {error_message}")
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    def delete_class(self, class_id):
        if not class_id:
            return self.generate_response(success=False, error='Class ID must be provided.', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                query = """
                    DELETE FROM classes
                    WHERE class_id = %s
                    RETURNING class_id;
                """
                cur.execute(query, (class_id,))
                deleted_class_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=200, data={'class_id': deleted_class_id})

            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                print(f"Error deleting class: {error_message}")
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