
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.config import Base
import enum


class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    nim = Column(String, unique=True, nullable=True)  # hanya untuk mahasiswa
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    hand_left_path = Column(String, nullable=True)
    hand_right_path = Column(String, nullable=True)
    hand_scan_class_index = Column(Integer, unique=True, nullable=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)

    class_students = relationship("ClassStudent", back_populates="student")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String, unique=True, nullable=False)  # id mk manual
    name = Column(String, nullable=False)
    semester = Column(String, nullable=False)  # Ganjil/Genap
    academic_year = Column(String, nullable=False)  # contoh: 2024/2025

    classes = relationship("Class", back_populates="course")


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # contoh: A, B, dst
    course_id = Column(Integer, ForeignKey("courses.id"))

    course = relationship("Course", back_populates="classes")
    class_students = relationship("ClassStudent", back_populates="class_")
    meetings = relationship("Meeting", back_populates="class_")


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    start_time = Column(String, nullable=False)  # format: "HH:MM"
    end_time = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"))

    class_ = relationship("Class", back_populates="meetings")
    attendances = relationship("Attendance", back_populates="meeting")


class ClassStudent(Base):
    __tablename__ = "class_students"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    student_id = Column(Integer, ForeignKey("users.id"))

    class_ = relationship("Class", back_populates="class_students")
    student = relationship("User", back_populates="class_students")
    attendances = relationship("Attendance", back_populates="class_student")


class AttendanceStatusEnum(str, enum.Enum):
    hadir = "Hadir"
    tidak_hadir = "Tidak Hadir"


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    class_student_id = Column(Integer, ForeignKey("class_students.id"))
    check_in_time = Column(DateTime, nullable=True)
    check_out_time = Column(DateTime, nullable=True)
    status = Column(Enum(AttendanceStatusEnum),
                    default=AttendanceStatusEnum.tidak_hadir)

    meeting = relationship("Meeting", back_populates="attendances")
    class_student = relationship("ClassStudent", back_populates="attendances")
