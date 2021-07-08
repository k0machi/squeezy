from database import db
from sqlalchemy import Column, Integer, String, Text, VARCHAR

class Settings(db.Model):
    id = Column(Integer, primary_key=True)
    key = Column(String(64), unique=True, nullable=False)
    value = Column(Text, unique=True, nullable=False)
    version = Column(VARCHAR(128))
