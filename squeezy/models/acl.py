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
    directives = db.relationship("ACLDirective", back_populates="acl")


class AccessDirective(db.Model):
    id = Column(Integer, primary_key=True)
    deny = Column(Boolean, nullable=False)
    type = Column(VARCHAR(32), nullable=False)
    priority = Column(Integer, nullable=False)
    acls = db.relationship("ACLDirective", back_populates="directive")


class ACLDirective(db.Model):
    __tablename__ = 'acl_directives'
    id = Column(Integer, primary_key=True, autoincrement=True)
    acl_id = Column(Integer, ForeignKey('access_control_list.id'), primary_key=True)
    directive_id = Column(Integer, ForeignKey('access_directive.id'), primary_key=True)
    negated = Column(Boolean, nullable=False)
    directive = db.relationship("AccessDirective", back_populates="acls")
    acl = db.relationship("AccessControlList", back_populates="directives")
