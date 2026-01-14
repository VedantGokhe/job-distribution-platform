# Job Distribution Platform – Indeed Integration (FastAPI)

This project implements a **centralized job distribution server** using **FastAPI**.
The goal is to allow HR or recruiters to:
- Create a job **once** using an API
- Store it centrally
- Automatically publish it to **Indeed** using an **XML job feed**

## Tech Stack

- Python 3.x
- FastAPI
- Uvicorn
- XML feeds for job aggregation

## Local Setup Instructions

### 1. Clone or extract the project

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the FastAPI server
```bash
python -m uvicorn main:app --reload
```

Server will start at:
```
http://localhost:8000
```

## Testing the Application Locally

### Step 1: Open Swagger UI
Open in browser:
```
http://localhost:8000/docs
```

### Step 2: Create a Job (POST /jobs)
Sample example:
```json
{
  "job_id": "JOB001",
  "title": "Data Scientist",
  "company": "DataMinds Analytics",
  "location": "Hyderabad, India",
  "description": "Seeking Data Scientist with expertise in Machine Learning, Python, and statistical modeling",
  "employment_type": "Full-time",
  "experience": "2-4 years",
  "salary": "₹10–16 LPA",
  "apply_url": "https://www.dataminds.com/careers/data-scientist"
}
```

### Step 3: Verify stored jobs
```
http://localhost:8000/jobs
```

### Step 4: Verify Indeed XML Feed
```
http://localhost:8000/feeds/indeed
```

## Deployment & Production Notes

- Indeed **cannot access localhost** environments.
- To enable real-world testing and publishing, the FastAPI server must be **deployed on a public URL** (e.g., AWS, Render, Railway, etc.).

### Example public feed URL:
```
https://jobs.companydomain.com/feeds/indeed
```

- Once deployed, this public feed URL must be submitted through the **Indeed Employer / Publisher onboarding process**.

### Indeed Employer Portal Submission Requires:
- **Company details**
- **Public job feed URL**
- **Official contact email address**

After submission and approval:
- Indeed periodically crawls the feed
- Jobs are published automatically on Indeed search results
- No manual job posting is required