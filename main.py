from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import engine, SessionLocal
from models import JobDB
from database import Base
import xml.etree.ElementTree as ET

app = FastAPI(title="Job Distribution Platform")

# Create DB tables
Base.metadata.create_all(bind=engine)

# =========================
# Pydantic Schema (API)
# =========================
class Job(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    description: str
    employment_type: str
    experience: str
    salary: str
    apply_url: str

# =========================
# DB Dependency
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# HR POSTS JOB ONCE
# =========================
@app.post("/jobs")
def create_job(job: Job, db: Session = Depends(get_db)):
    try:
        db_job = JobDB(**job.model_dump())
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return {
            "message": "Job stored successfully",
            "job_id": db_job.job_id
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Job ID already exists")

# =========================
# VIEW ALL JOBS
# =========================
@app.get("/jobs")
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobDB).all()
    return {
        "total_jobs": len(jobs),
        "jobs": jobs
    }

# =========================
# INDEED XML FEED
# =========================
@app.get("/feeds/indeed")
def indeed_feed(db: Session = Depends(get_db)):
    jobs = db.query(JobDB).all()

    root = ET.Element("jobs")
    for job in jobs:
        job_elem = ET.SubElement(root, "job")
        ET.SubElement(job_elem, "title").text = job.title
        ET.SubElement(job_elem, "company").text = job.company
        ET.SubElement(job_elem, "location").text = job.location
        ET.SubElement(job_elem, "description").text = job.description
        ET.SubElement(job_elem, "apply_url").text = job.apply_url

    xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return Response(content=xml, media_type="application/xml")
