from sqlalchemy import Column, String, Text
from database import Base

class JobDB(Base):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    employment_type = Column(String, nullable=False)
    experience = Column(String, nullable=False)
    salary = Column(String, nullable=False)
    apply_url = Column(String, nullable=False)
