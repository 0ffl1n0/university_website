from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor

import os  # <--- ADD THIS LINE

app = Flask(__name__)

# --- 1. DATABASE CONNECTION ---
# DELETE your old get_db_connection() and REPLACE it with this:
def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(database_url)
# This runs every time the app starts, so you don't need the Shell
from init_db import init_db
try:
    init_db()
    print("Database sync successful")
except Exception as e:
    print(f"Database sync failed: {e}")
    
# --- 2. NAVIGATION ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crud')
def crud_hub():
    return render_template('crud_hub.html')

# --- 3. THE 8 TABLE CRUD ROUTES ---

# 1. STUDENT (Already Fixed - Kept for Completeness)
@app.route('/students', methods=['GET', 'POST'])
def manage_students():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        cur.execute("""
            INSERT INTO public.student (last_name, first_name, dob, address, city, zip_code, phone, fax, email) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (request.form['last_name'], request.form['first_name'], request.form['dob'],
              request.form['address'], request.form['city'], request.form['zip_code'],
              request.form['phone'], request.form['fax'], request.form['email']))
        conn.commit()
        return redirect(url_for('manage_students'))
    cur.execute('SELECT * FROM public.student ORDER BY student_id DESC')
    students = cur.fetchall()
    cur.close(); conn.close()
    return render_template('students.html', students=students)

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        cur.execute("""
            UPDATE public.student SET last_name=%s, first_name=%s, dob=%s, address=%s, city=%s, zip_code=%s, phone=%s, fax=%s, email=%s 
            WHERE student_id=%s
        """, (request.form['last_name'], request.form['first_name'], request.form['dob'],
              request.form['address'], request.form['city'], request.form['zip_code'],
              request.form['phone'], request.form['fax'], request.form['email'], id))
        conn.commit(); cur.close(); conn.close()
        return redirect(url_for('manage_students'))
    cur.execute('SELECT * FROM public.student WHERE student_id = %s', (id,))
    student = cur.fetchone()
    cur.close(); conn.close()
    return render_template('edit_student.html', student=student)

@app.route('/delete_student/<int:id>')
def delete_student(id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute('DELETE FROM public.student WHERE student_id = %s', (id,))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for('manage_students'))

# 2. INSTRUCTOR
@app.route('/instructors', methods=['GET', 'POST'])
def manage_instructors():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        cur.execute("""
            INSERT INTO public.instructor (department_id, last_name, first_name, rank, phone, fax, email) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (request.form['dept_id'], request.form['last_name'], request.form['first_name'], 
              request.form['rank'], request.form['phone'], request.form['fax'], request.form['email']))
        conn.commit()
        return redirect(url_for('manage_instructors'))
    cur.execute('SELECT * FROM public.instructor ORDER BY instructor_id DESC')
    instructors = cur.fetchall()
    cur.close(); conn.close()
    return render_template('instructors.html', instructors=instructors)

@app.route('/edit_instructor/<int:id>', methods=['GET', 'POST'])
def edit_instructor(id):
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        cur.execute("""
            UPDATE public.instructor SET department_id=%s, last_name=%s, first_name=%s, rank=%s, phone=%s, fax=%s, email=%s 
            WHERE instructor_id=%s
        """, (request.form['dept_id'], request.form['last_name'], request.form['first_name'], 
              request.form['rank'], request.form['phone'], request.form['fax'], request.form['email'], id))
        conn.commit(); cur.close(); conn.close()
        return redirect(url_for('manage_instructors'))
    cur.execute('SELECT * FROM public.instructor WHERE instructor_id = %s', (id,))
    instructor = cur.fetchone()
    cur.close(); conn.close()
    return render_template('edit_instructor.html', instructor=instructor)

@app.route('/delete_instructor/<int:id>')
def delete_instructor(id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute('DELETE FROM public.instructor WHERE instructor_id = %s', (id,))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for('manage_instructors'))

# 3. DEPARTMENT
@app.route('/departments', methods=['GET', 'POST'])
def manage_departments():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        cur.execute("INSERT INTO public.department (department_id, name) VALUES (%s, %s)",
                    (request.form['dept_id'], request.form['name']))
        conn.commit()
        return redirect(url_for('manage_departments'))
    cur.execute('SELECT * FROM public.department ORDER BY department_id ASC')
    departments = cur.fetchall()
    cur.close(); conn.close()
    return render_template('departments.html', departments=departments)

@app.route('/edit_department/<int:id>', methods=['GET', 'POST'])
def edit_department(id):
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        cur.execute("UPDATE public.department SET name=%s WHERE department_id=%s", (request.form['name'], id))
        conn.commit(); cur.close(); conn.close()
        return redirect(url_for('manage_departments'))
    cur.execute('SELECT * FROM public.department WHERE department_id = %s', (id,))
    department = cur.fetchone()
    cur.close(); conn.close()
    return render_template('edit_department.html', department=department)

@app.route('/delete_department/<int:id>')
def delete_department(id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute('DELETE FROM public.department WHERE department_id = %s', (id,))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for('manage_departments'))

# 4. COURSE (Composite Key: course_id + department_id)
@app.route('/courses', methods=['GET', 'POST'])
def manage_courses():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        cur.execute("INSERT INTO public.course (course_id, department_id, name, description) VALUES (%s, %s, %s, %s)",
                    (request.form['course_id'], request.form['dept_id'], request.form['name'], request.form['desc']))
        conn.commit()
        return redirect(url_for('manage_courses'))
    cur.execute('SELECT * FROM public.course ORDER BY course_id ASC')
    courses = cur.fetchall()
    cur.close(); conn.close()
    return render_template('courses.html', courses=courses)

@app.route('/delete_course/<int:cid>/<int:did>')
def delete_course(cid, did):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute('DELETE FROM public.course WHERE course_id = %s AND department_id = %s', (cid, did))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for('manage_courses'))

# 5. ROOM (Composite Key: building + room_no)
@app.route('/rooms', methods=['GET', 'POST'])
def manage_rooms():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        cur.execute("INSERT INTO public.room (building, room_no, capacity) VALUES (%s, %s, %s)",
                    (request.form['building'], request.form['room_no'], request.form['capacity']))
        conn.commit()
        return redirect(url_for('manage_rooms'))
    cur.execute('SELECT * FROM public.room ORDER BY building, room_no')
    rooms = cur.fetchall()
    cur.close(); conn.close()
    return render_template('rooms.html', rooms=rooms)

@app.route('/delete_room/<bld>/<rm>')
def delete_room(bld, rm):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute('DELETE FROM public.room WHERE building = %s AND room_no = %s', (bld, rm))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for('manage_rooms'))

# 6. ENROLLMENT (Composite Primary Key)
@app.route('/enrollments', methods=['GET', 'POST'])
def manage_enrollments():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        cur.execute("INSERT INTO public.enrollment (student_id, course_id, department_id) VALUES (%s, %s, %s)",
                    (request.form['sid'], request.form['cid'], request.form['did']))
        conn.commit()
        return redirect(url_for('manage_enrollments'))
    cur.execute('SELECT * FROM public.enrollment ORDER BY enrollment_date DESC')
    enrollments = cur.fetchall()
    cur.close(); conn.close()
    return render_template('enrollments.html', enrollments=enrollments)

@app.route('/delete_enrollment/<int:sid>/<int:cid>/<int:did>')
def delete_enrollment(sid, cid, did):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute('DELETE FROM public.enrollment WHERE student_id=%s AND course_id=%s AND department_id=%s', (sid, cid, did))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for('manage_enrollments'))


# 7. MARK
@app.route('/marks', methods=['GET', 'POST'])
def manage_marks():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        cur.execute("""
            INSERT INTO public.mark (student_id, course_id, department_id, mark_type, value) 
            VALUES (%s, %s, %s, %s, %s)
        """, (request.form['sid'], request.form['cid'], request.form['did'], request.form['type'], request.form['val']))
        conn.commit()
        return redirect(url_for('manage_marks'))
    cur.execute('SELECT * FROM public.mark ORDER BY mark_id DESC')
    marks = cur.fetchall()
    cur.close(); conn.close()
    return render_template('marks.html', marks=marks)

@app.route('/delete_mark/<int:id>')
def delete_mark(id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute('DELETE FROM public.mark WHERE mark_id = %s', (id,))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for('manage_marks'))

# 8. RESERVATION
@app.route('/reservations', methods=['GET', 'POST'])
def manage_reservations():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        cur.execute("""
            INSERT INTO public.reservation (building, room_no, course_id, department_id, instructor_id, reserv_date, start_time, end_time, hours_number, reservation_purpose) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (request.form['bld'], request.form['rm'], request.form['cid'], request.form['did'], 
             request.form['iid'], request.form['date'], request.form['start'], request.form['end'], 
             request.form['hrs'], request.form['purpose']))
        conn.commit()
        return redirect(url_for('manage_reservations'))
    cur.execute('SELECT * FROM public.reservation ORDER BY reserv_date DESC')
    reservations = cur.fetchall()
    cur.close(); conn.close()
    return render_template('reservations.html', reservations=reservations)

@app.route('/delete_reservation/<int:id>')
def delete_reservation(id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute('DELETE FROM public.reservation WHERE reservation_id = %s', (id,))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for('manage_reservations'))

# --- ACADEMIC PLANNING HUB ---
@app.route('/planning')
def planning_hub():
    return render_template('planning_hub.html')

# --- ASSIGNMENT & RESERVATIONS ---
@app.route('/manage_assignments', methods=['GET', 'POST'])
def manage_assignments():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        # 1. Execute the Insert
        cur.execute("""
            INSERT INTO public.reservation 
            (building, room_no, course_id, department_id, instructor_id, reserv_date, start_time, end_time, hours_number, reservation_purpose) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (request.form['bld'], request.form['rm'], request.form['cid'], 
              request.form['did'], request.form['iid'], request.form['date'], 
              request.form['start'], request.form['end'], request.form['hrs'], 
              request.form['purpose']))
        
        conn.commit()
        cur.close()
        conn.close()
        # 2. Redirect back to the GET route to see the new data
        return redirect(url_for('manage_assignments'))

    # 3. This part handles the GET request (loading the page)
    cur.execute("""
        SELECT r.*, i.first_name, i.last_name, c.name as course_name 
        FROM public.reservation r
        JOIN public.instructor i ON r.instructor_id = i.instructor_id
        JOIN public.course c ON r.course_id = c.course_id AND r.department_id = c.department_id
        ORDER BY r.reserv_date DESC
    """)
    assignments = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('assignments.html', assignments=assignments)


# --- MODULE 3: MARKS & ATTENDANCE HUB ---
@app.route('/marks_hub')
def marks_hub():
    return render_template('marks_hub.html')

# --- MANAGE ATTENDANCE ---
@app.route('/attendance', methods=['GET', 'POST'])
def manage_attendance():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        # Assuming an 'attendance' table exists or using a log table
        # Logic: Insert student_id, course_id, date, and status (Present/Absent)
        # For now, we'll implement the view logic
        pass
    
    # Fetch student list and their recent attendance
    cur.execute("SELECT * FROM public.student")
    students = cur.fetchall()
    cur.close(); conn.close()
    return render_template('attendance.html', students=students)


    # --- MODULE 4: GRADING HUB ---
@app.route('/grading_hub')
def grading_hub():
    return render_template('grading_hub.html')

# --- RESULTS PROCESSING ---
@app.route('/process_results')
def process_results():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # SQL Logic: 
    # 1. 'averages' calculates the mean for every unique exam
    # 2. The main query joins students to their marks and compares them to 0.6 * average
    cur.execute("""
        WITH exam_stats AS (
            SELECT 
                course_id, 
                mark_type, 
                AVG(value) as avg_mark,
                AVG(value) * 0.6 as disqualifying_threshold
            FROM public.mark
            GROUP BY course_id, mark_type
        )
        SELECT 
            s.first_name, s.last_name, 
            c.name as course_name, 
            m.mark_type,
            m.value as student_mark,
            ROUND(stats.avg_mark, 2) as class_avg,
            ROUND(stats.disqualifying_threshold, 2) as dynamic_threshold
        FROM public.mark m
        JOIN public.student s ON m.student_id = s.student_id
        JOIN public.course c ON m.course_id = c.course_id AND m.department_id = c.department_id
        JOIN exam_stats stats ON m.course_id = stats.course_id AND m.mark_type = stats.mark_type
        ORDER BY c.name, m.mark_type, s.last_name;
    """)
    results = cur.fetchall()
    cur.close(); conn.close()
    return render_template('results.html', results=results)


    # --- MODULE 5: REPORTS HUB ---
@app.route('/reports_hub')
def reports_hub():
    return render_template('reports_hub.html')

@app.route('/report_a')
def report_a():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM public.student ORDER BY group_no, last_name")
    data = cur.fetchall()
    cur.close(); conn.close()
    return render_template('reports/generic_list.html', data=data, title="Students by Group")

# (b) List of students by section
@app.route('/report_b')
def report_b():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM public.student ORDER BY section, last_name")
    data = cur.fetchall()
    cur.close(); conn.close()
    return render_template('reports/generic_list.html', data=data, title="Students by Section")

# (c) Time table of each instructor
@app.route('/report_c')
def report_c():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT i.first_name, i.last_name, r.*, c.name as course_name 
        FROM public.reservation r 
        JOIN public.instructor i ON r.instructor_id = i.instructor_id
        JOIN public.course c ON r.course_id = c.course_id
        ORDER BY i.last_name, r.reserv_date, r.start_time
    """)
    data = cur.fetchall()
    cur.close(); conn.close()
    return render_template('reports/timetables.html', data=data, title="Instructor Timetables")

# (d) Student timetable by section, then by group
@app.route('/report_d')
def report_d():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # We join Reservation -> Course -> Enrollment -> Student 
    # to find which Section/Group should be in which Room.
    cur.execute("""
        SELECT DISTINCT
            s.section, 
            s.group_no, 
            r.building, 
            r.room_no, 
            r.reserv_date,
            r.start_time,
            r.end_time,
            c.name as course_name
        FROM public.reservation r
        JOIN public.course c ON r.course_id = c.course_id
        JOIN public.enrollment e ON c.course_id = e.course_id
        JOIN public.student s ON e.student_id = s.student_id
        ORDER BY s.section, s.group_no, r.reserv_date, r.start_time
    """)
    
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('reports/timetables.html', data=data, title="Student Timetables (By Section & Group)")
# (e) Students who passed the semester (Average >= 10)
@app.route('/report_e')
def report_e():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT s.first_name, s.last_name, AVG(m.value) as overall_avg
        FROM public.mark m JOIN public.student s ON m.student_id = s.student_id
        GROUP BY s.student_id, s.first_name, s.last_name
        HAVING AVG(m.value) >= 10
    """)
    data = cur.fetchall()
    cur.close(); conn.close()
    return render_template('reports/generic_list.html', data=data, title="Passed Semester")

# (f) List of disqualifying mark by module (0.6 * Class Average)

@app.route('/report_f')
def report_f():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    # Use ::FLOAT to cast the calculation result in PostgreSQL
    cur.execute("""
        SELECT 
            course_id, 
            mark_type, 
            (AVG(value) * 0.6)::FLOAT as threshold 
        FROM public.mark 
        GROUP BY course_id, mark_type
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('reports/thresholds.html', data=data)


# (h, i, j) Failing, Resit, and Excluded
@app.route('/report_hij/<type>')
def report_hij(type):
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    # This dynamic query filters based on the status we calculated earlier
    query = """
        WITH stats AS (SELECT course_id, mark_type, AVG(value)*0.6 as thr FROM public.mark GROUP BY course_id, mark_type)
        SELECT s.first_name, s.last_name, c.name as course_name, m.value, stats.thr
        FROM public.mark m JOIN public.student s ON m.student_id = s.student_id
        JOIN public.course c ON m.course_id = c.course_id JOIN stats ON m.course_id = stats.course_id
    """
    if type == 'excluded': query += " WHERE m.value < stats.thr"
    elif type == 'resit': query += " WHERE m.value >= stats.thr AND m.value < 10"
    
    cur.execute(query); data = cur.fetchall(); cur.close(); conn.close()
    return render_template('reports/generic_list.html', data=data, title=type.capitalize())

    # --- MODULE 6: AUDIT ---
@app.route('/audit')
def view_audit():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM public.audit_logs ORDER BY operation_time DESC")
    logs = cur.fetchall()
    cur.close(); conn.close()
    return render_template('audit_logs.html', logs=logs)

# Example of Report G using 5 functions (AVG, COUNT, MAX, MIN, ROUND)
@app.route('/report_g')
def report_g():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT 
            c.name as course,
            s.group_no,
            ROUND(AVG(m.value), 2) as average_mark,
            COUNT(m.mark_id) as total_entries,
            MAX(m.value) as highest_mark,
            MIN(m.value) as lowest_mark
        FROM public.mark m 
        JOIN public.student s ON m.student_id = s.student_id
        JOIN public.course c ON m.course_id = c.course_id
        GROUP BY c.name, s.group_no
    """)
    data = cur.fetchall()
    cur.close(); conn.close()
    return render_template('reports/generic_list.html', data=data, title="Group Statistics (Multi-Function Report)")



if __name__ == '__main__':

    app.run(debug=True)

