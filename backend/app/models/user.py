"""
SetuX / VeriX — User and Department ORM Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, synonym
from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="department_rel")
    projects = relationship("Project", back_populates="department_rel")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="officer", nullable=False)  # "officer" or "citizen"
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    department_name = Column(String(255), nullable=True)
    designation = Column(String(255), nullable=True)
    district = Column(String(100), nullable=True)
    employee_id = Column(String(100), nullable=True)
    last_login = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department_rel = relationship("Department", back_populates="users")

    name = synonym("full_name")

    @property
    def department(self):
        if self.department_rel:
            return self.department_rel
        return self.department_name

    @department.setter
    def department(self, val):
        if isinstance(val, str):
            self.department_name = val
        else:
            self.department_rel = val
