import os
from sqlalchemy import create_engine, Column, Text, Boolean, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import INSERT
from datetime import datetime

# Database connection URL
# Default to SQLite for local development if DATABASE_URL is not set
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # Use SQLite as fallback for local dev
    DATABASE_URL = "sqlite:///./jobs.db"

# SQLAlchemy requires 'postgresql://' instead of 'postgres://' (common in Render/Heroku)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(Text)
    employer = Column(Text)
    logo = Column(Text)
    city = Column(Text)
    state = Column(Text)
    country = Column(Text)
    description = Column(Text)
    apply_link = Column(Text)
    is_remote = Column(Boolean)
    employment_type = Column(Text)
    posted_at = Column(DateTime)
    raw_data = Column(Text)

def get_db_connection():
    # This now returns a SQLAlchemy engine for compatibility if needed, 
    # but we'll use SessionLocal for ORM operations.
    return engine.connect()

def init_db():
    Base.metadata.create_all(bind=engine)
    db_info = DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL
    print(f"Database initialized at {db_info}")

def upsert_job(job_data):
    db = SessionLocal()
    try:
        # Convert string timestamp to datetime object if needed
        posted_at = job_data.get('posted_at')
        if isinstance(posted_at, str) and posted_at:
            try:
                posted_at = datetime.fromisoformat(posted_at.replace('Z', '+00:00'))
            except ValueError:
                posted_at = None

        # Prepare values for PostgreSQL-style upsert or SQLAlchemy core
        stmt = INSERT(Job).values(
            id=job_data['id'],
            title=job_data['title'],
            employer=job_data['employer'],
            logo=job_data['logo'],
            city=job_data['city'],
            state=job_data['state'],
            country=job_data['country'],
            description=job_data['description'],
            apply_link=job_data['apply_link'],
            is_remote=job_data['is_remote'],
            employment_type=job_data['employment_type'],
            posted_at=posted_at,
            raw_data=job_data['raw_data']
        )
        
        # PostgreSQL ON CONFLICT DO UPDATE
        if DATABASE_URL.startswith("postgresql"):
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_={
                    'title': stmt.excluded.title,
                    'employer': stmt.excluded.employer,
                    'logo': stmt.excluded.logo,
                    'city': stmt.excluded.city,
                    'state': stmt.excluded.state,
                    'country': stmt.excluded.country,
                    'description': stmt.excluded.description,
                    'apply_link': stmt.excluded.apply_link,
                    'is_remote': stmt.excluded.is_remote,
                    'employment_type': stmt.excluded.employment_type,
                    'posted_at': stmt.excluded.posted_at,
                    'raw_data': stmt.excluded.raw_data
                }
            )
            db.execute(stmt)
        else:
            # Fallback for SQLite (local dev)
            existing_job = db.query(Job).filter(Job.id == job_data['id']).first()
            if existing_job:
                for key, value in job_data.items():
                    if key == 'posted_at':
                        setattr(existing_job, key, posted_at)
                    else:
                        setattr(existing_job, key, value)
            else:
                new_job = Job(**job_data)
                new_job.posted_at = posted_at
                db.add(new_job)
        
        db.commit()
    except Exception as e:
        print(f"Error upserting job {job_data.get('id')}: {e}")
        db.rollback()
    finally:
        db.close()
