# Job Distribution Platform – Indeed Integration (FastAPI)

This project implements a **centralized job distribution server** using **FastAPI**.
The goal is to allow HR or recruiters to:

- Create a job **once** using an API
- Store it centrally using a persistent database
- Automatically publish it to **Indeed** using an **XML job feed**

---

## Tech Stack

- Python 3.x
- FastAPI
- Uvicorn
- PostgreSQL (persistent storage)
- SQLAlchemy
- XML feeds for job aggregation
- Render (deployment)

---

## Local Setup Instructions

### 1. Clone or extract the project

```bash
git clone <repository-url>
cd job-distribution-platform
