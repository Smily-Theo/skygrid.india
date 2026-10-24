from sqlalchemy import Column, DateTime, Integer, String, Text
from .database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    kind = Column(String(80), nullable=False)
    severity = Column(String(20), nullable=False, default="INFO")
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True)
