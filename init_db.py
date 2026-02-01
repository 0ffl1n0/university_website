import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')

def init_db():
    if not DATABASE_URL:
        print("Error: DATABASE_URL environment variable is not set.")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    sql_script = """
    -- 1. DEPARTMENT
    CREATE TABLE IF NOT EXISTS public.department (
        department_id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL
    );

    -- 2. STUDENT
    CREATE TABLE IF NOT EXISTS public.student (
        student_id SERIAL PRIMARY KEY,
        last_name VARCHAR(100),
        first_name VARCHAR(100),
        dob DATE,
        address VARCHAR(255),
        city VARCHAR(100),
        zip_code VARCHAR(20),
        phone VARCHAR(20),
        fax VARCHAR(20),
        email VARCHAR(100) UNIQUE,
        group_no VARCHAR(10),
        section VARCHAR(10)
    );

    -- 3. COURSE
    CREATE TABLE IF NOT EXISTS public.course (
        course_id SERIAL,
        department_id INTEGER REFERENCES public.department(department_id),
        name VARCHAR(60) NOT NULL,
        description VARCHAR(1000),
        credits INTEGER,
        PRIMARY KEY (course_id, department_id)
    );

    -- 4. INSTRUCTOR
    CREATE TABLE IF NOT EXISTS public.instructor (
        instructor_id SERIAL PRIMARY KEY,
        last_name VARCHAR(50),
        first_name VARCHAR(50),
        email VARCHAR(100) UNIQUE,
        office_no VARCHAR(20),
        department_id INTEGER REFERENCES public.department(department_id)
    );

    -- 5. ROOM
    CREATE TABLE IF NOT EXISTS public.room (
        building VARCHAR(1) NOT NULL,
        room_no VARCHAR(10) NOT NULL,
        capacity INTEGER CHECK (capacity > 1),
        PRIMARY KEY (building, room_no)
    );

    -- 6. COURSE ACTIVITY
    CREATE TABLE IF NOT EXISTS public.course_activity (
        course_id INTEGER,
        dept_id INTEGER,
        activity_type VARCHAR(20),
        PRIMARY KEY (course_id, dept_id, activity_type),
        FOREIGN KEY (course_id, dept_id) REFERENCES public.course(course_id, department_id)
    );

    -- 7. ENROLLMENT
    CREATE TABLE IF NOT EXISTS public.enrollment (
        student_id INTEGER REFERENCES public.student(student_id),
        course_id INTEGER,
        dept_id INTEGER,
        enrollment_date DATE DEFAULT CURRENT_DATE,
        PRIMARY KEY (student_id, course_id, dept_id),
        FOREIGN KEY (course_id, dept_id) REFERENCES public.course(course_id, department_id)
    );

    -- 8. MARK
    CREATE TABLE IF NOT EXISTS public.mark (
        mark_id SERIAL PRIMARY KEY,
        student_id INTEGER REFERENCES public.student(student_id) ON DELETE CASCADE,
        course_id INTEGER,
        department_id INTEGER,
        mark_type VARCHAR(20) CHECK (mark_type IN ('Midterm', 'Final', 'Project', 'Quiz')),
        value NUMERIC(4,2) CHECK (value >= 0 AND value <= 20),
        date_recorded DATE DEFAULT CURRENT_DATE
    );

    -- 9. ATTENDANCE
    CREATE TABLE IF NOT EXISTS public.attendance (
        attendance_id SERIAL PRIMARY KEY,
        student_id INTEGER REFERENCES public.student(student_id) ON DELETE CASCADE,
        course_id INTEGER,
        dept_id INTEGER,
        attendance_date DATE,
        status VARCHAR(10),
        activity_type VARCHAR(20)
    );

    -- 10. RESERVATION
    CREATE TABLE IF NOT EXISTS public.reservation (
        reservation_id SERIAL PRIMARY KEY,
        course_id INTEGER,
        department_id INTEGER,
        instructor_id INTEGER REFERENCES public.instructor(instructor_id),
        building VARCHAR(1),
        room_no VARCHAR(10),
        day_of_week VARCHAR(10),
        start_time TIME,
        end_time TIME,
        FOREIGN KEY (course_id, department_id) REFERENCES public.course(course_id, department_id),
        FOREIGN KEY (building, room_no) REFERENCES public.room(building, room_no)
    );

    -- 11. AUDIT LOGS
    CREATE TABLE IF NOT EXISTS public.audit_logs (
        log_id SERIAL PRIMARY KEY,
        operation_type VARCHAR(10),
        operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        table_name VARCHAR(50),
        details TEXT
    );

    -- 12. MATERIALIZED VIEW
    DROP MATERIALIZED VIEW IF EXISTS public.mv_reservations_per_teacher;
    CREATE MATERIALIZED VIEW public.mv_reservations_per_teacher AS
    SELECT i.first_name, i.last_name, COUNT(r.reservation_id) as total_reservations
    FROM public.instructor i
    LEFT JOIN public.reservation r ON i.instructor_id = r.instructor_id
    GROUP BY i.instructor_id, i.first_name, i.last_name;
    """
    
    try:
        cur.execute(sql_script)
        conn.commit()
        print("Success: Database fully initialized with all 10 tables, view, and constraints!")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_db()
