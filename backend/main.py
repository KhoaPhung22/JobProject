from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = os.path.join(os.path.dirname(__file__), "..", "jobs.db")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
