import os
import psycopg2

# This gets the URL you just added to Render
DATABASE_URL = os.environ.get('DATABASE_URL')

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # The SQL script we need to run
    sql_script = """
    CREATE TABLE IF NOT EXISTS student (
        student_id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE
    );

    CREATE TABLE IF NOT EXISTS mark (
        mark_id SERIAL PRIMARY KEY,
        student_id INT REFERENCES student(student_id) ON DELETE CASCADE,
        subject VARCHAR(50),
        score DECIMAL(5,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        log_id SERIAL PRIMARY KEY,
        table_name VARCHAR(50),
        action VARCHAR(20),
        old_data JSONB,
        new_data JSONB,
        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cur.execute(sql_script)
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized!")

if __name__ == "__main__":
    init_db()