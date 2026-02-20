import sqlite3
import os

# Handle Render persistent storage or local dev
DB_PATH = os.environ.get("DATABASE_URL", os.path.join(os.path.dirname(__file__), "jobs.db"))
DB_NAME = DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            employer TEXT,
            logo TEXT,
            city TEXT,
            state TEXT,
            country TEXT,
            description TEXT,
            apply_link TEXT,
            is_remote BOOLEAN,
            employment_type TEXT,
            posted_at DATETIME,
            raw_data TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database {DB_NAME} initialized.")

def upsert_job(job_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO jobs (
                id, title, employer, logo, city, state, country, 
                description, apply_link, is_remote, employment_type, posted_at, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                employer=excluded.employer,
                logo=excluded.logo,
                city=excluded.city,
                state=excluded.state,
                country=excluded.country,
                description=excluded.description,
                apply_link=excluded.apply_link,
                is_remote=excluded.is_remote,
                employment_type=excluded.employment_type,
                posted_at=excluded.posted_at,
                raw_data=excluded.raw_data
        ''', (
            job_data['id'],
            job_data['title'],
            job_data['employer'],
            job_data['logo'],
            job_data['city'],
            job_data['state'],
            job_data['country'],
            job_data['description'],
            job_data['apply_link'],
            job_data['is_remote'],
            job_data['employment_type'],
            job_data['posted_at'],
            job_data['raw_data']
        ))
        conn.commit()
    except Exception as e:
        print(f"Error upserting job {job_data.get('id')}: {e}")
    finally:
        conn.close()
