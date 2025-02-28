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


# Database class to handle user information
class UserDatabase:
    def __init__(self, credentials_path='modules/database_modules/credentials.json'):
        self.credentials = load_db_credentials(credentials_path)

    def retrieve_user_info(self, user_id, user_type: str):
        if not user_id:
            return self.generate_response(success=False, error='User ID must be provided', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                if user_type == 'student':
                    query = """
                    SELECT name, username, faculty, matnum, email, birthdate
                    FROM users_students
                    WHERE id = %s;
                """

                elif user_type == 'teacher':
                    query = """
                    SELECT name, username, faculty, worknum, email, birthdate
                    FROM users_teachers
                    WHERE id = %s;
                """

                cur.execute(query, (user_id,))
                user_data = cur.fetchone()
                cur.close()
                user_data_dict = dict(user_data) if user_data else {}
                return self.generate_response(success=True, data=user_data_dict, status_code=200, error=None)

            except psycopg2.Error as e:
                error_msg = e.pgerror if e.pgerror else str(e)
                print(f'Error retrieving user information: {error_msg}')
                return self.generate_response(success=False, error=error_msg, status_code=500, error_code=e.pgcode)


    def modify_user_info(self, user_id, user_type: str, **kwargs):
        user_fields = ['name', 'username', 'password', 'email', 'matnum', 'worknum','faculty', 'birthdate']

        if not user_id:
            return self.generate_response(success=False, error='User ID must be provided', status_code=400)

        filtered_kwargs = {field: kwargs[field] for field in user_fields if field in kwargs}
        if not filtered_kwargs:
            return self.generate_response(success=False, error='No fields to update', status_code=400)

        # Validate required fields aren't being set to NULL or empty string
        non_nullable_fields = ['name', 'username', 'email']
        if user_type == 'student':
            non_nullable_fields.append('matnum')
        else:
            non_nullable_fields.append('worknum')

        for field in non_nullable_fields:
            if field in filtered_kwargs and (filtered_kwargs[field] is None or filtered_kwargs[field] == ""):
                return self.generate_response(success=False,
                                              error=f"Field '{field}' cannot be empty or null",
                                              status_code=400)

        # Validate worknum and matnum format
        if 'worknum' in filtered_kwargs and user_type == 'teacher':
            worknum = str(filtered_kwargs['worknum'])
            if not (worknum.isdigit() and len(worknum) == 6):
                return self.generate_response(success=False,
                                             error="Work number must be a 6-digit integer",
                                             status_code=400)

        if 'matnum' in filtered_kwargs and user_type == 'student':
            matnum = str(filtered_kwargs['matnum'])
            if not (matnum.isdigit() and len(matnum) == 7):
                return self.generate_response(success=False,
                                             error="Matriculation number must be a 7-digit integer",
                                             status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                table_name = f"users_{user_type}s"

                # Check for duplicate values
                fields_to_check = []
                if 'username' in filtered_kwargs:
                    fields_to_check.append(('username', filtered_kwargs['username']))
                if 'email' in filtered_kwargs:
                    fields_to_check.append(('email', filtered_kwargs['email']))
                if user_type == 'student' and 'matnum' in filtered_kwargs:
                    fields_to_check.append(('matnum', filtered_kwargs['matnum']))
                elif user_type == 'teacher' and 'worknum' in filtered_kwargs:
                    fields_to_check.append(('worknum', filtered_kwargs['worknum']))

                for field, value in fields_to_check:
                    query = f"SELECT id FROM {table_name} WHERE {field} = %s AND id != %s"
                    cur.execute(query, (str(value), str(user_id)))
                    existing_record = cur.fetchone()

                    if existing_record:
                        return self.generate_response(
                            success=False,
                            error=f"The {field} '{value}' is already registered to another user",
                            status_code=400
                        )

                # Build SET clause for update
                set_items = []
                params = []

                for field, value in filtered_kwargs.items():
                    # Skip fields that don't apply to this user type
                    if field == 'matnum' and user_type != 'student':
                        continue
                    if field == 'worknum' and user_type != 'teacher':
                        continue

                    set_items.append(f"{field} = %s")
                    params.append(value)

                if not set_items:
                    return self.generate_response(success=False,
                                                 error="No applicable fields to update",
                                                 status_code=400)

                set_clause = ", ".join(set_items)
                params.append(user_id)  # Add user_id for WHERE clause

                query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
                cur.execute(query, tuple(params))
                conn.commit()

                rows_affected = cur.rowcount
                cur.close()

                if rows_affected == 0:
                    return self.generate_response(success=False,
                                                 error=f"No {user_type} found with ID {user_id}",
                                                 status_code=404)

                return self.generate_response(success=True,
                                             data={'message': f"{user_type.capitalize()} information updated successfully"},
                                             status_code=200)

            except psycopg2.Error as e:
                conn.rollback()
                error_msg = e.pgerror if e.pgerror else str(e)
                print(f'Error updating user information: {error_msg}')
                return self.generate_response(success=False,
                                             error=error_msg,
                                             status_code=500,
                                             error_code=e.pgcode)

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
