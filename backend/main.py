from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import pandas as pd
from datetime import datetime


app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handle Render persistent storage or local dev
DB_PATH = os.environ.get("DATABASE_URL", os.path.join(os.path.dirname(__file__), "..", "jobs.db"))
DB_NAME = DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def read_root():
    return {"message": "Job Board API is running"}

@app.get("/jobs")
def get_jobs(
    search: str = Query(None, description="Search term for title or description"),
    location: str = Query(None, description="Filter by city, state, or country"),
    remote: bool = Query(None, description="Filter by remote jobs"),
    type: str = Query(None, description="Filter by employment type")
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []
    
    if search:
        query += " AND (title LIKE ? OR description LIKE ? OR employer LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])
        
    if location:
        query += " AND (city LIKE ? OR state LIKE ? OR country LIKE ?)"
        loc_term = f"%{location}%"
        params.extend([loc_term, loc_term, loc_term])
        
    if remote is not None:
        query += " AND is_remote = ?"
        params.append(remote)
        
    if type:
        query += " AND employment_type LIKE ?"
        params.append(f"%{type}%")
    
    cursor.execute(query, params)
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"count": len(jobs), "jobs": jobs}

@app.get("/analytics")
def get_analytics():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT title,posted_at,city, state, country, is_remote, employment_type FROM jobs", conn)
    print(df)
    conn.close()
    
    if df.empty:
        return {
            "total_jobs": 0,
            "remote_percent": 0,
            "top_cities": [],
            "employment_types": []
        }
    
    # Calculate stats
    total_jobs = len(df)
    remote_jobs = df['is_remote'].sum()
    remote_percent = (remote_jobs / total_jobs * 100) if total_jobs > 0 else 0
    
    # Top Cities
    top_cities = df['city'].value_counts().head(5).to_dict()
    top_cities_list = [{"name": name, "count": int(count)} for name, count in top_cities.items()]
    
    # Employment Types
    emp_types = df['employment_type'].value_counts().to_dict()
    emp_types_list = [{"type": name, "count": int(count)} for name, count in emp_types.items()]
    #Number of job related to Computer
    number_computer_jobs_df = df[df['title'].str.contains('Computer', case=False, na=False)]
    # Calculate jobs by day for the line chart
    jobs_by_day = pd.to_datetime(df['posted_at']).dt.date.astype(str).value_counts().sort_index().to_dict()
    number_of_jobs_by_days = [{"name": date, "count": int(count)} for date, count in jobs_by_day.items()]
    
    # Calculate jobs today for the stat card
    today_str = datetime.now().strftime('%Y-%m-%d')
    number_of_jobs_today = jobs_by_day.get(today_str, 0)
    
    print(f"Jobs today ({today_str}): {number_of_jobs_today}")
    
    return {
        "total_jobs": int(total_jobs),
        "remote_percent": round(float(remote_percent), 1),
        "top_cities": top_cities_list,
        "employment_types": emp_types_list,
        "number_computer_jobs": int(number_computer_jobs_df.shape[0]),
        "number_of_jobs_today": int(number_of_jobs_today),
        "number_of_jobs_by_days": number_of_jobs_by_days
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
