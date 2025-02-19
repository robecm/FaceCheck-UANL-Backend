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

        filtered_kwargs = {field: kwargs[field] for field in exam_fields + optional_fields if field in kwargs}
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                check_query = """
                    SELECT * FROM exams
                    WHERE exam_name = %(exam_name)s AND class_id = %(class_id)s;
                """
                cur.execute(check_query, filtered_kwargs)
                existing_exam = cur.fetchone()
                if existing_exam:
                    return self.generate_response(success=False, error='An exam with the same name already exists in the same class', status_code=400)

                columns = ', '.join(filtered_kwargs.keys())
                values = ', '.join([f'%({field})s' for field in filtered_kwargs.keys()])
                query = f"""
                    INSERT INTO exams ({columns})
                    VALUES ({values})
                    RETURNING exam_id;
                """
                cur.execute(query, filtered_kwargs)
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=201)
            except psycopg2.DatabaseError as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500)

    def update_exam(self, exam_id, **kwargs):
        exam_fields = ['exam_name', 'class_id']
        optional_fields = ['date', 'class_room', 'hour']
        if not exam_id:
            return self.generate_response(success=False, error='Exam ID must be provided', status_code=400)

        filtered_kwargs = {field: kwargs[field] for field in exam_fields + optional_fields if field in kwargs}
        if not filtered_kwargs:
            return self.generate_response(success=False, error='No fields to update', status_code=400)
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                check_query = """
                    SELECT * FROM exams
                    WHERE exam_id = %(exam_id)s;
                """
                cur.execute(check_query, {'exam_id': exam_id})
                existing_exam = cur.fetchone()
                if not existing_exam:
                    return self.generate_response(success=False, error='Exam not found', status_code=404)

                set_clause = ', '.join([f'{field} = %({field})s' for field in filtered_kwargs.keys()])
                query = f"""
                    UPDATE exams
                    SET {set_clause}
                    WHERE exam_id = %(exam_id)s
                    RETURNING exam_id;
                """
                filtered_kwargs['exam_id'] = exam_id
                cur.execute(query, filtered_kwargs)
                updated_class_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=200, data={'exam_id': updated_class_id})
            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    def delete_exam(self, exam_id):
        if not exam_id:
            return self.generate_response(success=False, error='Exam ID must be provided', status_code=400)
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
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
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    def modify_exam_results(self, results):
        if not results:
            return self.generate_response(
                success=False,
                error='No results provided',
                status_code=400
            )

        new_items = []
        update_items = []
        for item in results:
            if 'result_id' in item and item['result_id'] is not None:
                update_items.append(item)
            else:
                new_items.append(item)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Handle new items in one bulk insert with ON CONFLICT
                if new_items:
                    insert_values = []
                    value_placeholders = []
                    for row in new_items:
                        insert_values.extend([row['exam_id'], row['class_id'], row['student_id'], row['score']])
                        value_placeholders.append("(%s, %s, %s, %s)")
                    insert_query = f"""
                        INSERT INTO exam_results (exam_id, class_id, student_id, score)
                        VALUES {", ".join(value_placeholders)}
                        ON CONFLICT (exam_id, student_id)
                        DO UPDATE SET score = EXCLUDED.score;
                    """
                    cur.execute(insert_query, tuple(insert_values))

                # Handle existing items in one bulk update
                if update_items:
                    update_values = []
                    update_placeholders = []
                    for row in update_items:
                        update_values.extend([row['score'], row['result_id']])
                        update_placeholders.append("(%s, %s)")
                    update_query = f"""
                        UPDATE exam_results AS er
                        SET score = data.score
                        FROM (VALUES {", ".join(update_placeholders)})
                        AS data(score, result_id)
                        WHERE er.result_id = data.result_id;
                    """
                    cur.execute(update_query, tuple(update_values))

                conn.commit()
                cur.close()

                return self.generate_response(success=True, status_code=200)
            except psycopg2.DatabaseError as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500)

    def retrieve_exam_results(self, exam_id):
        if not exam_id:
            return self.generate_response(success=False, error='Exam ID must be provided', status_code=400)
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                check_query = """
                    SELECT exam_id, class_id FROM exams
                    WHERE exam_id = %s;
                """
                cur.execute(check_query, (exam_id,))
                if not cur.fetchone():
                    return self.generate_response(success=False, error='Exam not found', status_code=404)

                query = """
                    SELECT us.id AS student_id,
                           us.name AS student_name,
                           us.matnum AS student_matnum,
                           er.score
                    FROM classes_students cs
                    JOIN users_students us ON cs.student_id = us.id
                    JOIN exams e ON e.class_id = cs.class_id
                    LEFT JOIN exam_results er ON er.exam_id = e.exam_id
                                            AND er.student_id = us.id
                    WHERE e.exam_id = %s;
                """
                cur.execute(query, (exam_id,))
                data = cur.fetchall()
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=200, data=data)
            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    @staticmethod
    def generate_response(success, error=None, status_code=200, **kwargs):
        response = {
            'success': success,
            'error': error,
            'status_code': status_code
        }
        response.update(kwargs)
        return response