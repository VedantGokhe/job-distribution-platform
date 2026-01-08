from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.responses import Response

app = FastAPI(title="Job Distribution Platform")

# =========================
# COMMON JOB SCHEMA
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
# IN-MEMORY DATABASE
# =========================
jobs_db: List[Job] = []

# =========================
# HR POSTS JOB ONCE
# =========================
@app.post("/jobs")
def create_job(job: Job):
    jobs_db.append(job)
    return {
        "message": "Job stored successfully",
        "job": job
    }

# =========================
# VIEW ALL JOBS
# =========================
@app.get("/jobs")
def get_jobs():
    return {
        "total_jobs": len(jobs_db),
        "jobs": jobs_db
    }


@app.get("/feeds/indeed")
def indeed_feed():
    xml = "<jobs>"
    for job in jobs_db:
        xml += f"""
        <job>
            <title>{job.title}</title>
            <company>{job.company}</company>
            <location>{job.location}</location>
            <description>{job.description}</description>
            <apply_url>{job.apply_url}</apply_url>
        </job>
        """
    xml += "</jobs>"

    return Response(content=xml, media_type="application/xml")
