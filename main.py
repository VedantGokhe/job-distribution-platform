from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import Response, HTMLResponse
from fastapi.responses import PlainTextResponse 
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import engine, SessionLocal, Base
from models import JobDB
import xml.etree.ElementTree as ET
import json
from datetime import datetime, timedelta

app = FastAPI(title="Job Distribution Platform")


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="google-site-verification" content="h8SjOEZqUWqQu6W9DwxUJRgRU5ElY-RyuUAIH-0CETI">
        <title>Job Distribution Platform</title>
    </head>
    <body>
        <h1>Job Distribution Platform</h1>
        <p>This site hosts job postings for search engine indexing.</p>
    </body>
    </html>
    """


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


from fastapi import Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import json
from datetime import datetime, timedelta


@app.get("/jobs/{job_id}", response_class=HTMLResponse)
def job_detail_page(job_id: str, db: Session = Depends(get_db)):
    """
    Render a job detail page with Google JobPosting structured data.
    """
    # Fetch job from database
    job = db.query(JobDB).filter(JobDB.job_id == job_id).first()
    
    if not job:
        return HTMLResponse(
            content="<h1>Job not found</h1>", 
            status_code=404
        )
    
    # Dates for Google Jobs schema
    date_posted = datetime.utcnow().strftime("%Y-%m-%d")
    valid_through = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Build Google JobPosting JSON-LD structured data
    structured_data = {
        "@context": "https://schema.org/",
        "@type": "JobPosting",
        "title": job.title,
        "description": job.description,
        "identifier": {
            "@type": "PropertyValue",
            "name": job.company,
            "value": job.job_id
        },
        "datePosted": date_posted,
        "validThrough": valid_through,
        "employmentType": job.employment_type if hasattr(job, 'employment_type') else "FULL_TIME",
        "hiringOrganization": {
            "@type": "Organization",
            "name": job.company,
            "sameAs": "https://www.artizence.com",
            "logo": "https://www.artizence.com/logo.png"
        },
        "jobLocation": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": job.location if job.location.lower() != "remote" else "India",
                "addressCountry": "IN"
            }
        }
    }
    
    # Add remote job location type if applicable
    if job.location.lower() == "remote":
        structured_data["jobLocationType"] = "TELECOMMUTE"
        structured_data["applicantLocationRequirements"] = {
            "@type": "Country",
            "name": "IN"
        }
    
    # Add salary information if available
    if hasattr(job, 'salary') and job.salary:
        # Assuming salary is a string like "6-9 LPA" or a number
        structured_data["baseSalary"] = {
            "@type": "MonetaryAmount",
            "currency": "INR",
            "value": {
                "@type": "QuantitativeValue",
                "value": job.salary,
                "unitText": "YEAR"
            }
        }
    
    # Add direct apply URL if available
    if hasattr(job, 'apply_url') and job.apply_url:
        structured_data["directApply"] = True
    
    # HTML response with structured data
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="{job.title} position at {job.company}. {job.employment_type if hasattr(job, 'employment_type') else 'Full-time'} role in {job.location}.">
        
        <!-- Google JobPosting Structured Data -->
        <script type="application/ld+json">
{json.dumps(structured_data, indent=2)}
        </script>
        
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
            }}
            h3 {{
                color: #666;
                margin-top: 0;
            }}
            .job-meta {{
                background: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .job-meta p {{
                margin: 5px 0;
            }}
            button {{
                background-color: #007bff;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-top: 20px;
            }}
            button:hover {{
                background-color: #0056b3;
            }}
            a {{
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <h1>{job.title}</h1>
        <h3>{job.company}</h3>
        
        <div class="job-meta">
            <p><strong>Location:</strong> {job.location}</p>
            <p><strong>Experience:</strong> {job.experience if hasattr(job, 'experience') else 'Not specified'}</p>
            <p><strong>Employment Type:</strong> {job.employment_type if hasattr(job, 'employment_type') else 'Full-time'}</p>
            <p><strong>Salary:</strong> {job.salary if hasattr(job, 'salary') else 'Not disclosed'}</p>
        </div>
        
        <h2>Job Description</h2>
        <div>{job.description}</div>
        
        <a href="{job.apply_url if hasattr(job, 'apply_url') and job.apply_url else '#'}" target="_blank" rel="noopener noreferrer">
            <button>Apply Now</button>
        </a>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    return """User-agent: *
Allow: /
"""

@app.get("/sitemap.xml", response_class=Response)
def sitemap(db: Session = Depends(get_db)):
    jobs = db.query(JobDB).all()

    urlset = ET.Element(
        "urlset",
        xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    )

    # Home page
    url = ET.SubElement(urlset, "url")
    ET.SubElement(url, "loc").text = "https://job-distribution-platform.onrender.com/"
    ET.SubElement(url, "changefreq").text = "daily"
    ET.SubElement(url, "priority").text = "1.0"

    # Job pages
    for job in jobs:
        url = ET.SubElement(urlset, "url")
        ET.SubElement(
            url, "loc"
        ).text = f"https://job-distribution-platform.onrender.com/jobs/{job.job_id}"
        ET.SubElement(url, "changefreq").text = "daily"
        ET.SubElement(url, "priority").text = "0.9"

    xml = ET.tostring(urlset, encoding="utf-8", xml_declaration=True)
    return Response(content=xml, media_type="application/xml")

