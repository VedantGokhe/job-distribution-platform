from sqlalchemy import Column, String, Text
from database import Base

class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True, index=True)
    title = Column(String)
    company = Column(String)
    location = Column(String)
    description = Column(Text)
    employment_type = Column(String)
    experience = Column(String)
    salary = Column(String)
    apply_url = Column(String)
