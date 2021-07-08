from sqlalchemy.sql.expression import null
from sqlalchemy.sql.schema import ForeignKey
from database import db
from sqlalchemy import Column, String, Integer, VARCHAR, Text, Boolean

class AccessControlList(db.Model):
    id = Column(Integer, primary_key=True)
    label = Column(String(128), nullable=False)
    type = Column(VARCHAR(32), nullable=False)
    is_file = Column(Boolean, nullable=False)
    file_id = Column(Integer, ForeignKey("file.id"), nullable=True)
    parameters = Column(Text, nullable=True)
    priority = Column(Integer, nullable=False)
