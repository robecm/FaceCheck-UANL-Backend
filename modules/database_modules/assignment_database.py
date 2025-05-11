import psycopg2
import psycopg2.extras
import json
from contextlib import contextmanager


# Function to load database credentials from a JSON file
def load_credentials(path):
    with open(path, 'r') as f:
        return json.load(f)


# Context manager for the database connection
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


# Database class to handle operations related to assignments and their evidences
class AssignmentsDatabase:
    def __init__(self, credentials_path='modules/database_modules/credentials.json'):
        self.credentials = load_credentials(credentials_path)

    # Create an assignment in the assignments table
    def create_assignment(self, **kwargs):
        assignment_fields = ['title', 'class_id', 'due_date']
        optional_fields = ['description']
        if not all(field in kwargs for field in assignment_fields):
            return self.generate_response(success=False, error='The fields title, class_id, due_date are required.',
                                          status_code=400)

        filtered_kwargs = {field: kwargs[field] for field in assignment_fields + optional_fields if field in kwargs}

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                # Verify that the class exists
                check_class_query = "SELECT 1 FROM classes WHERE class_id = %s;"
                cur.execute(check_class_query, (filtered_kwargs['class_id'],))
                if not cur.fetchone():
                    return self.generate_response(success=False, error='Class not found.', status_code=404)

                # Avoid duplicate assignments with the same title in the same class
                check_query = "SELECT 1 FROM assignments WHERE title = %s AND class_id = %s;"
                cur.execute(check_query, (filtered_kwargs['title'], filtered_kwargs['class_id']))
                if cur.fetchone():
                    return self.generate_response(success=False,
                                                  error='An assignment with the same title already exists in this class.',
                                                  status_code=400)

                columns = ', '.join(filtered_kwargs.keys())
                values = ', '.join([f'%({field})s' for field in filtered_kwargs.keys()])
                query = f"""
                    INSERT INTO assignments ({columns})
                    VALUES ({values})
                    RETURNING assignment_id;
                """
                cur.execute(query, filtered_kwargs)
                assignment_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=201,
                                              data={'assignment_id': assignment_id})
            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)


    def update_assignment(self, assignment_id, **kwargs):
        if not assignment_id:
            return self.generate_response(success=False, error='The assignment_id must be provided.', status_code=400)

        allowed_fields = ['title', 'description', 'due_date', 'class_id']
        filtered_kwargs = {field: kwargs[field] for field in allowed_fields if field in kwargs}
        if not filtered_kwargs:
            return self.generate_response(success=False, error='No fields provided for update.', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                # Verify that the assignment exists and retrieve current values
                cur.execute("SELECT title, due_date, class_id FROM assignments WHERE assignment_id = %s;", (assignment_id,))
                record = cur.fetchone()
                if not record:
                    cur.close()
                    return self.generate_response(success=False, error='Assignment not found.', status_code=404)

                current_title, current_due_date, current_class_id = record
                # Determine new values after update, using provided values or current ones
                new_title = filtered_kwargs.get('title', current_title)
                new_due_date = filtered_kwargs.get('due_date', current_due_date)

                # Check that the updated assignment doesn't match another existing one (title and due_date)
                check_query = """
                    SELECT 1 FROM assignments
                    WHERE title = %(title)s AND due_date = %(due_date)s
                      AND assignment_id != %(assignment_id)s;
                """
                cur.execute(check_query, {
                    'title': new_title,
                    'due_date': new_due_date,
                    'assignment_id': assignment_id
                })
                if cur.fetchone():
                    cur.close()
                    return self.generate_response(
                        success=False,
                        error='An assignment with the same title and due date already exists.',
                        status_code=400
                    )

                # If the class is being updated, verify that the new class exists
                if 'class_id' in filtered_kwargs:
                    cur.execute("SELECT 1 FROM classes WHERE class_id = %s;", (filtered_kwargs['class_id'],))
                    if not cur.fetchone():
                        cur.close()
                        return self.generate_response(success=False, error='New class not found.', status_code=404)

                # Construct the update query
                set_clause = ', '.join([f'{field} = %({field})s' for field in filtered_kwargs.keys()])
                query = f"""
                    UPDATE assignments
                    SET {set_clause}
                    WHERE assignment_id = %(assignment_id)s
                    RETURNING assignment_id;
                """
                filtered_kwargs['assignment_id'] = assignment_id
                cur.execute(query, filtered_kwargs)
                updated_assignment_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=200,
                                              data={'assignment_id': updated_assignment_id})
            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)

    # Delete an assignment
    def delete_assignment(self, assignment_id):
        if not assignment_id:
            return self.generate_response(success=False, error='The assignment_id must be provided.', status_code=400)
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                # Verify that the assignment exists
                check_query = "SELECT 1 FROM assignments WHERE assignment_id = %s;"
                cur.execute(check_query, (assignment_id,))
                if not cur.fetchone():
                    return self.generate_response(success=False, error='Assignment not found.', status_code=404)

                query = """
                    DELETE FROM assignments
                    WHERE assignment_id = %s
                    RETURNING assignment_id;
                """
                cur.execute(query, (assignment_id,))
                deleted_assignment_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=200,
                                              data={'assignment_id': deleted_assignment_id})
            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)


    def retrieve_class_assignments(self, class_id):
        if not class_id:
            return self.generate_response(success=False, error='The class_id must be provided.', status_code=400)
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                # Verify that the class exists
                check_query = "SELECT 1 FROM classes WHERE class_id = %s;"
                cur.execute(check_query, (class_id,))
                if not cur.fetchone():
                    return self.generate_response(success=False, error='Class not found.', status_code=404)

                query = "SELECT * FROM assignments WHERE class_id = %s;"
                cur.execute(query, (class_id,))
                assignments = cur.fetchall()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=200, data=assignments)
            except psycopg2.Error as e:
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500, error_code=e.pgcode)


    def retrieve_student_assignments(self, student_id):
        if not student_id:
            return self.generate_response(success=False, error='Student ID must be provided', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

                # Check if student exists
                check_query = """
                    SELECT 1 FROM users_students
                    WHERE id = %s;
                """
                cur.execute(check_query, (student_id,))
                if not cur.fetchone():
                    return self.generate_response(success=False, error='Student not found', status_code=404)

                # Retrieve assignments for classes the student is enrolled in
                query = """
                    SELECT a.assignment_id, a.title, a.description, a.due_date, 
                           a.class_id, c.class_name, c.semester, ut.name as teacher_name,
                           (SELECT COUNT(*) > 0 FROM assignments_evidences 
                            WHERE assignment_id = a.assignment_id AND student_id = %s) as submitted
                    FROM assignments a
                    JOIN classes c ON a.class_id = c.class_id
                    JOIN users_teachers ut ON c.teacher_id = ut.id
                    JOIN classes_students cs ON c.class_id = cs.class_id
                    WHERE cs.student_id = %s
                    ORDER BY a.due_date DESC;
                """
                cur.execute(query, (student_id, student_id))
                assignments = cur.fetchall()

                return self.generate_response(success=True, error=None, status_code=200, data=assignments)

            except psycopg2.Error as e:
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500)

    def retrieve_teacher_assignments(self, teacher_id):
        if not teacher_id:
            return self.generate_response(success=False, error='Teacher ID must be provided', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

                # Check if teacher exists
                check_query = """
                    SELECT 1 FROM users_teachers
                    WHERE id = %s;
                """
                cur.execute(check_query, (teacher_id,))
                if not cur.fetchone():
                    return self.generate_response(success=False, error='Teacher not found', status_code=404)

                # Retrieve assignments for classes taught by the teacher
                query = """
                    SELECT a.assignment_id, a.title, a.description, a.due_date, 
                           a.class_id, c.class_name, c.semester, c.group_num,
                           (SELECT COUNT(*) FROM assignments_evidences
                            WHERE assignment_id = a.assignment_id) as submissions_count
                    FROM assignments a
                    JOIN classes c ON a.class_id = c.class_id
                    WHERE c.teacher_id = %s
                    ORDER BY a.due_date DESC;
                """
                cur.execute(query, (teacher_id,))
                assignments = cur.fetchall()

                return self.generate_response(success=True, error=None, status_code=200, data=assignments)

            except psycopg2.Error as e:
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False, error=error_message, status_code=500)


    def upload_assignment_evidence(self, **kwargs):
        """
        Upload evidence for an assignment with file metadata.

        Args:
            assignment_id: ID of the assignment
            student_id: ID of the student submitting the evidence
            class_id: ID of the class for this assignment
            file_data: Binary data of the uploaded file
            file_name: Original name of the file (optional)
            file_extension: Extension of the file (optional)

        Returns:
            dict: Response containing success status and evidence ID if successful
        """
        # Required fields
        required_fields = ['assignment_id', 'student_id', 'class_id', 'file_data']

        # Check required fields
        if not all(field in kwargs for field in required_fields):
            return self.generate_response(
                success=False,
                error='The fields assignment_id, student_id, class_id, and file_data are required.',
                status_code=400
            )

        # Include all possible fields (required + optional)
        all_fields = required_fields + ['file_name', 'file_extension']
        filtered_kwargs = {field: kwargs[field] for field in all_fields if field in kwargs}

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()

                # Verify entities exist
                cur.execute("SELECT 1 FROM assignments WHERE assignment_id = %s;", (filtered_kwargs['assignment_id'],))
                if not cur.fetchone():
                    return self.generate_response(success=False, error='Assignment not found.', status_code=404)

                cur.execute("SELECT 1 FROM users_students WHERE id = %s;", (filtered_kwargs['student_id'],))
                if not cur.fetchone():
                    return self.generate_response(success=False, error='Student not found.', status_code=404)

                cur.execute("SELECT 1 FROM classes WHERE class_id = %s;", (filtered_kwargs['class_id'],))
                if not cur.fetchone():
                    return self.generate_response(success=False, error='Class not found.', status_code=404)

                # Build dynamic query
                columns = ', '.join(filtered_kwargs.keys())
                placeholders = ', '.join([f'%({field})s' for field in filtered_kwargs])

                query = f"""
                    INSERT INTO assignments_evidences ({columns})
                    VALUES ({placeholders})
                    RETURNING evidence_id;
                """

                cur.execute(query, filtered_kwargs)
                evidence_id = cur.fetchone()[0]
                conn.commit()
                cur.close()

                return self.generate_response(
                    success=True,
                    error=None,
                    status_code=201,
                    data={'evidence_id': evidence_id}
                )

            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(
                    success=False,
                    error=error_message,
                    status_code=500,
                    error_code=e.pgcode
                )


    def remove_assignment_evidence(self, evidence_id):
        if not evidence_id:
            return self.generate_response(success=False, error='The evidence_id must be provided.', status_code=400)
        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                # Verify that the evidence exists
                cur.execute("SELECT 1 FROM assignments_evidences WHERE evidence_id = %s;", (evidence_id,))
                if not cur.fetchone():
                    return self.generate_response(success=False, error='Evidence not found.', status_code=404)
                # Delete the evidence record completely
                query = """
                    DELETE FROM assignments_evidences
                    WHERE evidence_id = %(evidence_id)s
                    RETURNING evidence_id;
                """
                cur.execute(query, {'evidence_id': evidence_id})
                deleted_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=200,
                                             data={'evidence_id': deleted_id})
            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False,
                                             error=error_message,
                                             status_code=500,
                                             error_code=e.pgcode)


    def grade_assignment_evidence(self, evidence_id, grade, feedback=None):
        """
        Grade an assignment evidence and optionally add feedback.

        Args:
            evidence_id: ID of the evidence to grade
            grade: Numeric grade to assign
            feedback (optional): Text feedback for the student

        Returns:
            dict: Response containing success status, data or error message
        """
        if not evidence_id:
            return self.generate_response(success=False, error='The evidence_id must be provided.', status_code=400)
        if grade is None:
            return self.generate_response(success=False, error='Grade must be provided.', status_code=400)

        # Create parameters dictionary and SET clause
        params = {'grade': grade, 'evidence_id': evidence_id}
        set_clause = "grade = %(grade)s"

        # Add feedback to parameters if provided
        if feedback is not None:
            params['feedback'] = feedback
            set_clause += ", feedback = %(feedback)s"

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM assignments_evidences WHERE evidence_id = %s;", (evidence_id,))
                if not cur.fetchone():
                    return self.generate_response(success=False, error='Evidence not found.', status_code=404)

                query = f"""
                    UPDATE assignments_evidences
                    SET {set_clause}
                    WHERE evidence_id = %(evidence_id)s
                    RETURNING evidence_id;
                """
                cur.execute(query, params)
                updated_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                return self.generate_response(success=True, error=None, status_code=200,
                                              data={'evidence_id': updated_id})
            except psycopg2.Error as e:
                conn.rollback()
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(success=False,
                                              error=error_message,
                                              status_code=500,
                                              error_code=e.pgcode)


    def get_assignment_evidences(self, assignment_id):
        """
        Retrieve all evidence submissions for a specific assignment.

        Args:
            assignment_id: ID of the assignment to get evidences for

        Returns:
            dict: Response containing success status and evidence data if successful
        """
        if not assignment_id:
            return self.generate_response(success=False, error='The assignment_id must be provided.', status_code=400)

        with db_connection(self.credentials) as conn:
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

                # Verify assignment exists
                cur.execute("SELECT 1 FROM assignments WHERE assignment_id = %s;", (assignment_id,))
                if not cur.fetchone():
                    return self.generate_response(success=False, error='Assignment not found.', status_code=404)

                # Retrieve evidences with student information
                query = """
                    SELECT ae.evidence_id, ae.assignment_id, ae.student_id, 
                           ae.class_id, ae.file_data, ae.grade, ae.feedback,
                           ae.file_name, ae.file_extension,
                           us.name as student_name, us.username as student_username
                    FROM assignments_evidences ae
                    JOIN users_students us ON ae.student_id = us.id
                    WHERE ae.assignment_id = %s
                    ORDER BY ae.evidence_id DESC;
                """
                cur.execute(query, (assignment_id,))
                evidences = cur.fetchall()
                cur.close()

                return self.generate_response(success=True, error=None, status_code=200, data=evidences)

            except psycopg2.Error as e:
                error_message = e.pgerror if e.pgerror else str(e)
                return self.generate_response(
                    success=False,
                    error=error_message,
                    status_code=500,
                    error_code=e.pgcode
                )


    # Private method to generate consistent JSON responses
    @staticmethod
    def generate_response(success, error=None, status_code=200, **kwargs):
        response = {
            'success': success,
            'error': error,
            'status_code': status_code
        }
        response.update(kwargs)
        return response
