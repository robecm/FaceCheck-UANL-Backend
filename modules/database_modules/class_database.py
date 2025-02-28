import psycopg2
import psycopg2.extras
import json
from contextlib import contextmanager
from datetime import time


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
    def __init__(self, credentials_path='modules/database_modules/credentials.json'):
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

                # Check if the teacher exists
                check_query = """
                    SELECT 1 FROM users_teachers
                    WHERE id = %s;
                """
                cur.execute(check_query, (filtered_kwargs['teacher_id'],))
                existing_teacher = cur.fetchone()
                if not existing_teacher:
                    return self.generate_response(success=False, error='Teacher not found.', status_code=404)

                # Check if the class already exists
                check_query = """
                    SELECT 1 FROM classes
                    WHERE class_name = %s AND teacher_id = %s AND group_num = %s AND semester = %s;
                """
                cur.execute(check_query,
                            (filtered_kwargs['class_name'], filtered_kwargs['teacher_id'],
                             filtered_kwargs['group_num'], filtered_kwargs['semester']))
                existing_class = cur.fetchone()
                if existing_class:
                    return self.generate_response(success=False, error='Class already exists.', status_code=400)

                # Insert the class data into the database
                columns = ', '.join(filtered_kwargs.keys())
                values = ', '.join([f'%({field})s' for field in filtered_kwargs.keys()])
                query = f"""
                    INSERT INTO classes ({columns})
                    VALUES ({values})
                    RETURNING class_id;
                """
                cur.execute(query, filtered_kwargs)
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

    def retrieve_class_students(self, class_id):
        if not class_id:
            return self.generate_response(success=False, error='Class ID must be provided.', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                # Check if the class exists
                check_query = """
                    SELECT 1 FROM classes
                    WHERE class_id = %s;
                """
                cur.execute(check_query, (class_id,))
                existing_class = cur.fetchone()
                if not existing_class:
                    return self.generate_response(success=False, error='Class not found.', status_code=404)

                # Retrieve the students registered in the class
                query = """
                    SELECT users_students.id, name, username, email, faculty, matnum
                    FROM users_students
                    JOIN classes_students ON users_students.id = classes_students.student_id
                    WHERE class_id = %s;
                """
                cur.execute(query, (class_id,))
                students = cur.fetchall()
                cur.close()
                students_dict = [dict(row) for row in students]
                return self.generate_response(success=True, error=None, status_code=200, data=students_dict)

            except psycopg2.Error as e:
                error_message = e.pgerror if e.pgerror else str(e)
                print(f"Error retrieving class students: {error_message}")
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

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

                # Check if the class exists
                check_query = """
                    SELECT 1 FROM classes
                    WHERE class_id = %s;
                """
                cur.execute(check_query, (class_id,))
                existing_class = cur.fetchone()
                if not existing_class:
                    return self.generate_response(success=False, error='Class not found.', status_code=404)

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

                # Check if the class exists
                check_query = """
                    SELECT 1 FROM classes
                    WHERE class_id = %s;
                """
                cur.execute(check_query, (class_id,))
                existing_class = cur.fetchone()
                if not existing_class:
                    return self.generate_response(success=False, error='Class not found.', status_code=404)

                # Delete the class
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

    def add_student_to_class(self, matnum, class_id):
        if not matnum or not class_id:
            return self.generate_response(success=False, error='Both matnum and class ID must be provided.', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Check if the class exists
                check_query = """
                    SELECT 1 FROM classes
                    WHERE class_id = %s;
                """
                cur.execute(check_query, (class_id,))
                existing_class = cur.fetchone()
                if not existing_class:
                    return self.generate_response(success=False, error='Class not found.', status_code=404)

                # Check if the student exists and retrieve the student ID
                check_query = """
                    SELECT id FROM users_students
                    WHERE matnum = %s;
                """
                cur.execute(check_query, (str(matnum),))  # Convert matnum to string
                existing_student = cur.fetchone()
                if not existing_student:
                    return self.generate_response(success=False, error='Student not found.', status_code=404)

                student_id = existing_student[0]

                # Check if the student is already registered in the class
                query = """
                    SELECT 1 FROM classes_students
                    WHERE student_id = %s AND class_id = %s;
                """
                cur.execute(query, (student_id, class_id))
                existing_registration = cur.fetchone()
                if existing_registration:
                    return self.generate_response(success=False, error='Student is already registered in the class.', status_code=400)

                # Insert the student into the class
                query = """
                    INSERT INTO classes_students (student_id, class_id)
                    VALUES (%s, %s)
                    RETURNING student_id, class_id;
                """
                cur.execute(query, (student_id, class_id))
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=201)

            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                print(f"Error adding student to class: {error_message}")
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    def del_student_from_class(self, student_id, class_id):
        if not student_id or not class_id:
            return self.generate_response(success=False, error='Both student ID and class ID must be provided.', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Check if the class exists
                check_query = """
                    SELECT 1 FROM classes
                    WHERE class_id = %s;
                """
                cur.execute(check_query, (class_id,))
                existing_class = cur.fetchone()
                if not existing_class:
                    return self.generate_response(success=False, error='Class not found.', status_code=404)

                # Check if the student exists
                check_query = """
                    SELECT 1 FROM users_students
                    WHERE id = %s;
                """
                cur.execute(check_query, (student_id,))
                existing_student = cur.fetchone()
                if not existing_student:
                    return self.generate_response(success=False, error='Student not found.', status_code=404)

                # Check if the student is registered in the class
                check_query = """
                    SELECT 1 FROM classes_students
                    WHERE student_id = %s AND class_id = %s;
                """
                cur.execute(check_query, (student_id, class_id))
                if not cur.fetchone():
                    return self.generate_response(success=False, error='Student is not registered in the class.', status_code=404)

                # Proceed to delete the student from the class
                delete_query = """
                    DELETE FROM classes_students
                    WHERE student_id = %s AND class_id = %s
                    RETURNING student_id, class_id;
                """
                cur.execute(delete_query, (student_id, class_id))
                result = cur.fetchone()
                deleted_student = result[0]
                deleted_class = result[1]
                conn.commit()
                cur.close()

                return self.generate_response(success=True, error=None, status_code=200, data={'student_id': deleted_student, 'class_id': deleted_class})

            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                print(f"Error deleting student from class: {error_message}")
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    def retrieve_class_exams(self, class_id):
        if not class_id:
            return self.generate_response(success=False, error='Class ID must be provided.', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                # Check if the class exists
                check_query = """
                    SELECT 1 FROM classes
                    WHERE class_id = %s;
                """
                cur.execute(check_query, (class_id,))
                existing_class = cur.fetchone()
                if not existing_class:
                    return self.generate_response(success=False, error='Class not found.', status_code=404)

                # Retrieve the exams for the class
                query = """
                    SELECT * FROM exams
                    WHERE class_id = %s;
                """
                cur.execute(query, (class_id,))
                exams = cur.fetchall()
                cur.close()

                if not exams:
                    return self.generate_response(success=False, error='No exams found for the class.', status_code=404)

                exams_dict = [dict(row) for row in exams]

                # Convert time objects to strings
                for exam in exams_dict:
                    for key, value in exam.items():
                        if isinstance(value, time):
                            exam[key] = value.strftime('%H:%M:%S')

                return self.generate_response(success=True, error=None, status_code=200, data=exams_dict)

            except psycopg2.Error as e:
                error_message = e.pgerror if e.pgerror else str(e)
                print(f"Error retrieving class exams: {error_message}")
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
