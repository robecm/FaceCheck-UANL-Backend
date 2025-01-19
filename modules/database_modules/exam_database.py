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

                # Check if there is already an exam with the same name in the same class
                check_query = """
                    SELECT * FROM exams
                    WHERE exam_name = %(exam_name)s AND class_id = %(class_id)s;
                """
                cur.execute(check_query, filtered_kwargs)
                existing_exam = cur.fetchone()
                if existing_exam:
                    return self.generate_response(success=False, error='An exam with the same name already exists in the same class', status_code=400)

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

    def update_exam(self, exam_id, **kwargs):
        exam_fields = ['exam_name', 'class_id']
        optional_fields = ['date', 'class_room', 'hour']

        if not exam_id:
            return self.generate_response(success=False, error='Exam ID must be provided', status_code=400)

        # Filter out optional fields that are not provided
        filtered_kwargs = {field: kwargs[field] for field in exam_fields + optional_fields if field in kwargs}

        if not filtered_kwargs:
            return self.generate_response(success=False, error='No fields to update', status_code=400)
        print('Received data:', filtered_kwargs)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Check if the exam exists
                check_query = """
                    SELECT * FROM exams
                    WHERE exam_id = %(exam_id)s;
                """
                cur.execute(check_query, {'exam_id': exam_id})
                existing_exam = cur.fetchone()
                if not existing_exam:
                    return self.generate_response(success=False, error='Exam not found', status_code=404)

                # Construct the update query
                set_clause = ', '.join([f'{field} = %({field})s' for field in filtered_kwargs.keys()])
                query = f"""
                    UPDATE exams
                    SET {set_clause}
                    WHERE exam_id = %(exam_id)s
                    RETURNING exam_id;
                """
                filtered_kwargs['exam_id'] = exam_id
                cur.execute(query, filtered_kwargs)
                print('Exam updated successfully')  # Debugging print

                updated_class_id = cur.fetchone()[0]
                print('Updated exam ID:', updated_class_id)  # Debugging print
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=200, data={'exam_id': updated_class_id})

            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                print(f'Error updating exam: {error_message}')
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    def delete_exam(self, exam_id):
        if not exam_id:
            return self.generate_response(success=False, error='Exam ID must be provided', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Check if the exam exists
                check_query = """
                    SELECT * FROM exams
                    WHERE exam_id = %s;
                """
                cur.execute(check_query, (exam_id,))
                existing_exam = cur.fetchone()
                if not existing_exam:
                    return self.generate_response(success=False, error='Exam not found', status_code=404)

                query = """
                    DELETE FROM exams
                    WHERE exam_id = %s
                    RETURNING exam_id;
                """
                cur.execute(query, (exam_id,))
                deleted_exam_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=200, data={'exam_id': deleted_exam_id})

            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                print(f'Error deleting exam: {error_message}')
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    def add_exam_result(self, exam_id, class_id, student_id, score):
        if not all([exam_id, class_id, student_id, score]):
            return self.generate_response(success=False, error='All required fields must be provided', status_code=400)

        with db_connection(self.credentials) as conn:

            try:
                cur = conn.cursor()

                # Check if the class has the exam and the student
                check_query = """
                    SELECT * FROM exams
                    WHERE exam_id = %s AND class_id = %s;
                """
                cur.execute(check_query, (exam_id, class_id))
                existing_exam = cur.fetchone()
                if not existing_exam:
                    return self.generate_response(success=False, error='Exam not found in the class', status_code=404)

                check_query = """
                    SELECT * FROM classes_students
                    WHERE student_id = %s AND class_id = %s;
                """
                cur.execute(check_query, (student_id, class_id))
                existing_student = cur.fetchone()
                if not existing_student:
                    return self.generate_response(success=False, error='Student not found in the class', status_code=404)

                # Check if the student has already taken the exam
                check_query = """
                    SELECT * FROM exam_results
                    WHERE exam_id = %s AND student_id = %s;
                """
                cur.execute(check_query, (exam_id, student_id))
                existing_score = cur.fetchone()
                if existing_score:
                    return self.generate_response(success=False, error='Student has already taken the exam', status_code=400)

                # Insert the score into the database
                query = """
                    INSERT INTO exam_results (exam_id, class_id, student_id, score)
                    VALUES (%s, %s, %s, %s)
                    RETURNING result_id;
                """
                cur.execute(query, (exam_id, class_id, student_id, score))
                print('Score added successfully')  # Debugging print

                result_id = cur.fetchone()[0]
                print('Generated result ID:', result_id)  # Debugging print
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=201)

            except psycopg2.DatabaseError as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                print(f'Error adding score: {error_message}') # Debugging print
                return self.generate_response(success=False, error=error_message, status_code=500)

    def update_exam_result(self, result_id, score):
        if not all([result_id, score]):
            return self.generate_response(success=False, error='All required fields must be provided', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Check if the result exists
                check_query = """
                    SELECT * FROM exam_results
                    WHERE result_id = %s;
                """
                cur.execute(check_query, (result_id,))
                existing_result = cur.fetchone()
                if not existing_result:
                    return self.generate_response(success=False, error='Result not found', status_code=404)

                # Update the score
                query = """
                    UPDATE exam_results
                    SET score = %s
                    WHERE result_id = %s
                    RETURNING result_id;
                """
                cur.execute(query, (score, result_id))
                print('Score updated successfully')  # Debugging print

                updated_result_id = cur.fetchone()[0]
                print('Updated result ID:', updated_result_id)  # Debugging print
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=200, data={'result_id': updated_result_id})

            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                print(f'Error updating score: {error_message}')
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    def retrieve_exam_results(self, exam_id):
        if not exam_id:
            return self.generate_response(success=False, error='Exam ID must be provided', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

                # Check if the exam exists
                check_query = """
                    SELECT * FROM exams
                    WHERE exam_id = %s;
                """
                cur.execute(check_query, (exam_id,))
                existing_exam = cur.fetchone()
                if not existing_exam:
                    return self.generate_response(success=False, error='Exam not found', status_code=404)

                # Retrieve the exam results
                query = """
                    SELECT * FROM exam_results
                    WHERE exam_id = %s;
                """
                cur.execute(query, (exam_id,))
                results = cur.fetchall()
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=200, data=results)

            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                print(f'Error retrieving exam results: {error_message}')
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    def delete_exam_result(self, result_id):
        if not result_id:
            return self.generate_response(success=False, error='Result ID must be provided', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Check if the result exists
                check_query = """
                    SELECT * FROM exam_results
                    WHERE result_id = %s;
                """
                cur.execute(check_query, (result_id,))
                existing_result = cur.fetchone()
                if not existing_result:
                    return self.generate_response(success=False, error='Result not found', status_code=404)

                # Delete the result
                query = """
                    DELETE FROM exam_results
                    WHERE result_id = %s
                    RETURNING result_id;
                """
                cur.execute(query, (result_id,))
                deleted_result_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=200, data={'result_id': deleted_result_id})

            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                print(f'Error deleting result: {error_message}')
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