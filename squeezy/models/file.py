from sqlalchemy.sql.expression import null
from database import db
from sqlalchemy import Column, String, Integer, VARCHAR, Text


class File(db.Model):
    id = Column(Integer, primary_key=True)
    label = Column(String(128), nullable=False)
    filepath = Column(String(4096), nullable=False)
    original_filename = Column(String(255), nullable=False)
    sha256 = Column(String(256), nullable=False)
