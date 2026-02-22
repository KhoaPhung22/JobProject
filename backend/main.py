from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
import os
import pandas as pd
from datetime import datetime
from database import SessionLocal, Job, init_db

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"message": "Job Board API is running"}

@app.get("/jobs")
def get_jobs(
    search: str = Query(None, description="Search term for title or description"),
    location: str = Query(None, description="Filter by city, state, or country"),
    remote: bool = Query(None, description="Filter by remote jobs"),
    type: str = Query(None, description="Filter by employment type"),
    db: Session = Depends(get_db)
):
    query = db.query(Job)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(
            Job.title.ilike(search_term),
            Job.description.ilike(search_term),
            Job.employer.ilike(search_term)
        ))
        
    if location:
        loc_term = f"%{location}%"
        query = query.filter(or_(
            Job.city.ilike(loc_term),
            Job.state.ilike(loc_term),
            Job.country.ilike(loc_term)
        ))
        
    if remote is not None:
        query = query.filter(Job.is_remote == remote)
        
    if type:
        query = query.filter(Job.employment_type.ilike(f"%{type}%"))
    
    jobs_list = query.all()
    
    return {
        "count": len(jobs_list),
        "jobs": [
            {
                "id": j.id,
                "title": j.title,
                "employer": j.employer,
                "logo": j.logo,
                "city": j.city,
                "state": j.state,
                "country": j.country,
                "description": j.description,
                "apply_link": j.apply_link,
                "is_remote": j.is_remote,
                "employment_type": j.employment_type,
                "posted_at": j.posted_at,
            } for j in jobs_list
        ]
    }

@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    # Using pandas for complex analytics as before, but fetching via SQLAlchemy
    jobs_query = db.query(Job).all()
    
    if not jobs_query:
        return {
            "total_jobs": 0,
            "remote_percent": 0,
            "top_cities": [],
            "employment_types": []
        }
    
    # Convert to DataFrame
    data = []
    for j in jobs_query:
        data.append({
            "title": j.title,
            "posted_at": j.posted_at,
            "city": j.city,
            "state": j.state,
            "country": j.country,
            "is_remote": j.is_remote,
            "employment_type": j.employment_type
        })
    df = pd.DataFrame(data)
    
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
    
    # Number of job related to Computer
    number_computer_jobs_df = df[df['title'].str.contains('Computer', case=False, na=False)]
    
    # Calculate jobs by day
    df['posted_date'] = pd.to_datetime(df['posted_at']).dt.date
    jobs_by_day = df['posted_date'].astype(str).value_counts().sort_index().to_dict()
    number_of_jobs_by_days = [{"name": date, "count": int(count)} for date, count in jobs_by_day.items()]
    
    # Calculate jobs today
    today_str = datetime.now().date().isoformat()
    number_of_jobs_today = int(jobs_by_day.get(today_str, 0))
    
    return {
        "total_jobs": int(total_jobs),
        "remote_percent": round(float(remote_percent), 1),
        "top_cities": top_cities_list,
        "employment_types": emp_types_list,
        "number_computer_jobs": int(len(number_computer_jobs_df)),
        "number_of_jobs_today": number_of_jobs_today,
        "number_of_jobs_by_days": number_of_jobs_by_days
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
