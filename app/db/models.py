from sqlalchemy import Column, String, Integer, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    s3_key = Column(String)
    schema = Column(Text)
    upload_time = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    file_size_kb = Column(Float, nullable=True)
