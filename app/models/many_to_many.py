from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.database import Base

association_table = Table('association', Base.metadata,
                          Column('student_id', Integer, ForeignKey('students.id')),
                          Column('course_id', Integer, ForeignKey('courses.id'))
                          )

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    courses = relationship("Course", secondary=association_table, back_populates="students")

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    students = relationship("Student", secondary=association_table, back_populates="courses")