import psycopg2
import psycopg2.extras
import json
from contextlib import contextmanager
from datetime import date, time

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

class AttendanceDatabase:
    def __init__(self, credentials_path='modules/database_modules/credentials.json'):
        self.credentials = load_db_credentials(credentials_path)

    def create_attendance(self, class_id, student_id, attendance_date, attendance_time=None, present=True):
        """
        Inserts a new attendance record into the attendance table.
        Expected parameters:
          - class_id: ID of the class.
          - student_id: ID of the student.
          - attendance_date: The date of attendance (as a string 'YYYY-MM-DD' or date object).
          - attendance_time: (Optional) The time of attendance (as a string 'HH:MM:SS' or time object).
          - present: Boolean indicating if the student is present.
        """
        query = """
            INSERT INTO attendance (class_id, student_id, date, time, present)
            VALUES (%(class_id)s, %(student_id)s, %(date)s, %(time)s, %(present)s)
            RETURNING attendance_id;
        """
        params = {
            'class_id': class_id,
            'student_id': student_id,
            'date': attendance_date if isinstance(attendance_date, str) else attendance_date.strftime('%Y-%m-%d'),
            'time': (attendance_time if isinstance(attendance_time, str)
                     else attendance_time.strftime('%H:%M:%S')) if attendance_time else None,
            'present': present
        }
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                cur.execute(query, params)
                attendance_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                return self.generate_response(success=True, data={'attendance_id': attendance_id}, status_code=201)
            except psycopg2.DatabaseError as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500)

    def update_attendance(self, attendance_id, **kwargs):
        """
        Updates an existing attendance record. Acceptable keys in kwargs:
          - class_id, student_id, date, time, present.
        """
        if not kwargs:
            return self.generate_response(success=False, error='No fields provided to update.', status_code=400)
        set_clause = ', '.join([f"{field} = %({field})s" for field in kwargs.keys()])
        query = f"""
            UPDATE attendance
            SET {set_clause}
            WHERE attendance_id = %(attendance_id)s
            RETURNING attendance_id;
        """
        kwargs['attendance_id'] = attendance_id
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                cur.execute(query, kwargs)
                updated_record = cur.fetchone()
                if not updated_record:
                    conn.rollback()
                    return self.generate_response(success=False, error='Attendance record not found.', status_code=404)
                conn.commit()
                cur.close()
                return self.generate_response(success=True, data={'attendance_id': updated_record[0]}, status_code=200)
            except psycopg2.DatabaseError as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500)

    def delete_attendance(self, attendance_id):
        """
        Deletes an attendance record based on its ID.
        """
        query = """
            DELETE FROM attendance
            WHERE attendance_id = %s
            RETURNING attendance_id;
        """
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                cur.execute(query, (attendance_id,))
                deleted = cur.fetchone()
                if not deleted:
                    conn.rollback()
                    return self.generate_response(success=False, error='Attendance record not found.', status_code=404)
                conn.commit()
                cur.close()
                return self.generate_response(success=True, data={'attendance_id': deleted[0]}, status_code=200)
            except psycopg2.DatabaseError as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500)

    def get_attendance_by_student(self, student_id):
        """
        Retrieves all attendance records for a specific student.
        """
        query = """
            SELECT * FROM attendance
            WHERE student_id = %s;
        """
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute(query, (student_id,))
                records = cur.fetchall()
                cur.close()

                # Convert datetime objects to strings for JSON serialization
                data = []
                for record in records:
                    record_dict = dict(record)
                    if 'date' in record_dict and record_dict['date']:
                        record_dict['date'] = record_dict['date'].isoformat()
                    if 'time' in record_dict and record_dict['time']:
                        record_dict['time'] = record_dict['time'].isoformat()
                    data.append(record_dict)

                return self.generate_response(success=True, data=data, status_code=200)
            except psycopg2.DatabaseError as e:
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500)

    def get_attendance_by_class(self, class_id):
        """
        Retrieves all attendance records for a specific class.
        """
        query = """
            SELECT * FROM attendance
            WHERE class_id = %s;
        """
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute(query, (class_id,))
                records = cur.fetchall()
                cur.close()

                # Convert datetime objects to strings for JSON serialization
                data = []
                for record in records:
                    record_dict = dict(record)
                    if 'date' in record_dict and record_dict['date']:
                        record_dict['date'] = record_dict['date'].isoformat()
                    if 'time' in record_dict and record_dict['time']:
                        record_dict['time'] = record_dict['time'].isoformat()
                    data.append(record_dict)

                return self.generate_response(success=True, data=data, status_code=200)
            except psycopg2.DatabaseError as e:
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500)

    @staticmethod
    def generate_response(success, error=None, status_code=200, **kwargs):
        response = {
            'success': success,
            'error': error,
            'status_code': status_code
        }
        response.update(kwargs)
        return response