from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.db.database import Base

association_table = Table(
    "student_course",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id")),
    Column("course_id", Integer, ForeignKey("courses.id")),
)


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    courses = relationship(
        "Course", secondary=association_table, back_populates="students"
    )


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    students = relationship(
        "Student", secondary=association_table, back_populates="courses"
    )


student1 = Student(name="John Doe")
student2 = Student(name="Jane Doe")
course1 = Course(title="Python")
course2 = Course(title="SQL")
