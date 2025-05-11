"""
Database module for user information management.

This module provides functionality to interact with the user database for operations
such as retrieving and modifying user information for both students and teachers.
"""

import psycopg2
import psycopg2.extras
import json
from contextlib import contextmanager


def load_db_credentials(path):
    """
    Load database credentials from a JSON file.

    Args:
        path (str): Path to the JSON file containing database credentials.

    Returns:
        dict: A dictionary containing database connection parameters.
    """
    with open(path, 'r') as file:
        return json.load(file)


@contextmanager
def db_connection(credentials):
    """
    Context manager for database connections.

    Creates a connection using the provided credentials and yields it.
    Ensures proper connection cleanup after use.

    Args:
        credentials (dict): Database connection parameters.

    Yields:
        psycopg2.connection: An active database connection.

    Raises:
        psycopg2.DatabaseError: If connection fails.
    """
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


class UserDatabase:
    """
    Database class to handle user information operations.

    This class provides methods to retrieve and modify user information
    for both students and teachers in the database.
    """

    def __init__(self, credentials_path='modules/database_modules/credentials.json'):
        """
        Initialize the UserDatabase with database credentials.

        Args:
            credentials_path (str): Path to the JSON file containing database credentials.
                                   Defaults to 'modules/database_modules/credentials.json'.
        """
        self.credentials = load_db_credentials(credentials_path)

    def retrieve_user_info(self, user_id, user_type: str):
        """
        Retrieve user information from the database.

        Args:
            user_id (str): The ID of the user to retrieve.
            user_type (str): The type of user ('student' or 'teacher').

        Returns:
            dict: A response dictionary containing success status, data, error message,
                 and status code.
        """
        if not user_id:
            return self.generate_response(
                success=False,
                error='User ID must be provided',
                status_code=400
            )

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
                result = cur.fetchone()
                cur.close()

                user_data = dict(result) if result else {}
                # Format birthdate to DD-MM-YYYY if it exists
                if user_data.get("birthdate"):
                    user_data["birthdate"] = user_data["birthdate"].strftime("%d-%m-%Y")

                return self.generate_response(
                    success=True,
                    data=user_data,
                    status_code=200,
                    error=None
                )

            except psycopg2.Error as e:
                error_msg = e.pgerror if e.pgerror else str(e)
                print(f'Error retrieving user information: {error_msg}')
                return self.generate_response(
                    success=False,
                    error=error_msg,
                    status_code=500,
                    error_code=e.pgcode
                )

    def modify_user_info(self, user_id, user_type: str, **kwargs):
        """
        Modify user information in the database.

        Args:
            user_id (str): The ID of the user to modify.
            user_type (str): The type of user ('student' or 'teacher').
            **kwargs: Fields to update (name, username, password, email, etc.).

        Returns:
            dict: A response dictionary containing success status, data/error message,
                 and status code.
        """
        user_fields = [
            'name', 'username', 'password', 'email',
            'matnum', 'worknum', 'faculty', 'birthdate'
        ]

        if not user_id:
            return self.generate_response(
                success=False,
                error='User ID must be provided',
                status_code=400
            )

        filtered_kwargs = {
            field: kwargs[field] for field in user_fields if field in kwargs
        }
        if not filtered_kwargs:
            return self.generate_response(
                success=False,
                error='No fields to update',
                status_code=400
            )

        # Handle empty birthdate - convert to None for SQL NULL
        if 'birthdate' in filtered_kwargs and filtered_kwargs['birthdate'] == '':
            filtered_kwargs['birthdate'] = None

        # Validate required fields aren't being set to NULL or empty string
        non_nullable_fields = ['name', 'username', 'email']
        if user_type == 'student':
            non_nullable_fields.append('matnum')
        else:
            non_nullable_fields.append('worknum')

        for field in non_nullable_fields:
            if field in filtered_kwargs and (
                filtered_kwargs[field] is None or filtered_kwargs[field] == ""
            ):
                return self.generate_response(
                    success=False,
                    error=f"Field '{field}' cannot be empty or null",
                    status_code=400
                )

        # Validate worknum and matnum format
        if 'worknum' in filtered_kwargs and user_type == 'teacher':
            worknum = str(filtered_kwargs['worknum'])
            if not (worknum.isdigit() and len(worknum) == 6):
                return self.generate_response(
                    success=False,
                    error="Work number must be a 6-digit integer",
                    status_code=400
                )

        if 'matnum' in filtered_kwargs and user_type == 'student':
            matnum = str(filtered_kwargs['matnum'])
            if not (matnum.isdigit() and len(matnum) == 7):
                return self.generate_response(
                    success=False,
                    error="Matriculation number must be a 7-digit integer",
                    status_code=400
                )

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
                    return self.generate_response(
                        success=False,
                        error="No applicable fields to update",
                        status_code=400
                    )

                set_clause = ", ".join(set_items)
                params.append(user_id)  # Add user_id for WHERE clause

                query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
                cur.execute(query, tuple(params))
                conn.commit()

                rows_affected = cur.rowcount
                cur.close()

                if rows_affected == 0:
                    return self.generate_response(
                        success=False,
                        error=f"No {user_type} found with ID {user_id}",
                        status_code=404
                    )

                return self.generate_response(
                    success=True,
                    data={'message': f"{user_type.capitalize()} information updated successfully"},
                    status_code=200
                )

            except psycopg2.Error as e:
                conn.rollback()
                error_msg = e.pgerror if e.pgerror else str(e)
                print(f'Error updating user information: {error_msg}')
                return self.generate_response(
                    success=False,
                    error=error_msg,
                    status_code=500,
                    error_code=e.pgcode
                )

    @staticmethod
    def generate_response(success, error=None, status_code=200, **kwargs):
        """
        Generate a consistent JSON response.

        Args:
            success (bool): Whether the operation was successful.
            error (str, optional): Error message. Defaults to None.
            status_code (int, optional): HTTP status code. Defaults to 200.
            **kwargs: Additional data to include in the response.

        Returns:
            dict: A formatted response dictionary.
        """
        response = {
            'success': success,
            'error': error,
            'status_code': status_code
        }
        response.update(kwargs)
        return response