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

    def modify_attendance(self, class_id, student_id, attendance_date, attendance_time=None, present=True):
        """
        Creates or updates attendance records. If a record exists for the student on
        the given date and class, it updates it. Otherwise, creates a new record.

        Args:
            class_id: ID of the class
            student_id: Can be a single student ID or a list of student IDs
            attendance_date: The date of attendance (string or date object)
            attendance_time: Optional time of attendance (string or time object)
            present: Boolean indicating if students are present

        Returns:
            dict: Response with success status and results
        """
        # Determine if handling multiple students
        multiple_students = isinstance(student_id, list)

        # Format date and time parameters
        formatted_date = attendance_date if isinstance(attendance_date, str) else attendance_date.strftime('%Y-%m-%d')
        formatted_time = None
        if attendance_time:
            formatted_time = attendance_time if isinstance(attendance_time, str) else attendance_time.strftime('%H:%M:%S')

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Validate student(s) exist
                student_ids = student_id if multiple_students else [student_id]
                if not student_ids:
                    return self.generate_response(success=False, error="No student IDs provided", status_code=400)

                # Check if all student IDs exist
                placeholders = ', '.join(['%s'] * len(student_ids))
                check_query = f"""
                    SELECT id FROM users_students
                    WHERE id IN ({placeholders})
                """
                cur.execute(check_query, student_ids)
                found_ids = [str(row[0]) for row in cur.fetchall()]

                missing_ids = [str(sid) for sid in student_ids if str(sid) not in found_ids]
                if missing_ids:
                    return self.generate_response(
                        success=False,
                        error=f"The following student IDs do not exist: {', '.join(missing_ids)}",
                        status_code=404
                    )

                # Process each student
                created_ids = []
                updated_ids = []

                for sid in student_ids:
                    # Check if attendance record already exists
                    cur.execute("""
                        SELECT attendance_id FROM attendance 
                        WHERE student_id = %s AND class_id = %s AND date = %s
                    """, (sid, class_id, formatted_date))

                    existing = cur.fetchone()

                    if existing:
                        # Update existing record
                        attendance_id = existing[0]
                        cur.execute("""
                            UPDATE attendance
                            SET time = %s, present = %s
                            WHERE attendance_id = %s
                            RETURNING attendance_id
                        """, (formatted_time, present, attendance_id))
                        updated_ids.append(cur.fetchone()[0])
                    else:
                        # Create new record
                        cur.execute("""
                            INSERT INTO attendance (class_id, student_id, date, time, present)
                            VALUES (%s, %s, %s, %s, %s)
                            RETURNING attendance_id
                        """, (class_id, sid, formatted_date, formatted_time, present))
                        created_ids.append(cur.fetchone()[0])

                conn.commit()
                cur.close()

                return self.generate_response(
                    success=True,
                    data={
                        'created_attendance_ids': created_ids,
                        'updated_attendance_ids': updated_ids
                    },
                    status_code=201
                )

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