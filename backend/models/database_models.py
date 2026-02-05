"""
SQLAlchemy Database Models
Maps to the PostgreSQL schema created in Phase 1
"""
from sqlalchemy import Column, String, Integer, DECIMAL, Boolean, DateTime, ForeignKey, CheckConstraint, Text, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from utils.database import Base
import uuid

class Student(Base):
    """Student model - core student information"""
    __tablename__ = 'students'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    roll_number = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    branch = Column(String(50), nullable=False, index=True)
    batch_year = Column(Integer, nullable=False, index=True)
    current_semester = Column(Integer, CheckConstraint('current_semester BETWEEN 1 AND 8'))
    cgpa = Column(DECIMAL(3, 2), CheckConstraint('cgpa BETWEEN 0 AND 10'))
    account_status = Column(String(20), default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    courses = relationship("StudentCourse", back_populates="student", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="student", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="student", cascade="all, delete-orphan")
    internships = relationship("Internship", back_populates="student", cascade="all, delete-orphan")
    assessments = relationship("SkillAssessment", back_populates="student", cascade="all, delete-orphan")
    role_matches = relationship("StudentRoleMatch", back_populates="student", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Student {self.roll_number} - {self.full_name}>"


class Course(Base):
    """Course catalog"""
    __tablename__ = 'courses'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_code = Column(String(20), unique=True, nullable=False)
    course_name = Column(String(150), nullable=False)
    branch = Column(String(50), nullable=False)
    semester = Column(Integer, CheckConstraint('semester BETWEEN 1 AND 8'))
    credits = Column(Integer, CheckConstraint('credits BETWEEN 1 AND 6'))
    course_type = Column(String(30))
    syllabus_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student_courses = relationship("StudentCourse", back_populates="course")
    
    def __repr__(self):
        return f"<Course {self.course_code} - {self.course_name}>"


class Skill(Base):
    """Skills taxonomy"""
    __tablename__ = 'skills'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_name = Column(String(100), unique=True, nullable=False, index=True)
    skill_category = Column(String(50), nullable=False)
    description = Column(Text)
    branches = Column(JSONB)
    benchmark_score = Column(Integer, CheckConstraint('benchmark_score BETWEEN 0 AND 100'), default=70)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student_skills = relationship("StudentSkill", back_populates="skill")
    assessments = relationship("SkillAssessment", back_populates="skill")
    
    def __repr__(self):
        return f"<Skill {self.skill_name}>"


class StudentSkill(Base):
    """Student skill scores with evidence"""
    __tablename__ = 'student_skills'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    raw_score = Column(Integer, CheckConstraint('raw_score BETWEEN 0 AND 100'))
    weighted_score = Column(DECIMAL(5, 2), CheckConstraint('weighted_score BETWEEN 0 AND 100'))
    confidence_level = Column(DECIMAL(3, 2), CheckConstraint('confidence_level BETWEEN 0 AND 1'))
    evidence_sources = Column(JSONB)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="skills")
    skill = relationship("Skill", back_populates="student_skills")
    
    __table_args__ = (
        CheckConstraint('raw_score BETWEEN 0 AND 100'),
        CheckConstraint('weighted_score BETWEEN 0 AND 100'),
    )
    
    def __repr__(self):
        return f"<StudentSkill {self.student_id} - {self.skill_id}: {self.weighted_score}>"


class IndustryRole(Base):
    """Industry role definitions"""
    __tablename__ = 'industry_roles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_title = Column(String(100), unique=True, nullable=False, index=True)
    role_category = Column(String(50))
    description = Column(Text)
    required_skills = Column(JSONB, nullable=False)
    eligible_branches = Column(JSONB)
    avg_ctc = Column(DECIMAL(10, 2))
    demand_score = Column(Integer, CheckConstraint('demand_score BETWEEN 0 AND 100'))
    typical_companies = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student_matches = relationship("StudentRoleMatch", back_populates="role")
    
    def __repr__(self):
        return f"<Role {self.role_title}>"


class StudentRoleMatch(Base):
    """Cached role match scores"""
    __tablename__ = 'student_role_matches'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('industry_roles.id', ondelete='CASCADE'), nullable=False)
    match_score = Column(DECIMAL(5, 2), CheckConstraint('match_score BETWEEN 0 AND 100'))
    missing_skills = Column(JSONB)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="role_matches")
    role = relationship("IndustryRole", back_populates="student_matches")
    
    def __repr__(self):
        return f"<RoleMatch {self.student_id} - {self.role_id}: {self.match_score}%>"


class SkillAssessment(Base):
    """Skill assessments (quiz, project, certification, etc.)"""
    __tablename__ = 'skill_assessments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    assessment_type = Column(String(20), nullable=False)
    score = Column(Integer, CheckConstraint('score BETWEEN 0 AND 100'))
    assessment_metadata = Column(JSONB)  # Renamed from 'metadata' (reserved word)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="assessments")
    skill = relationship("Skill", back_populates="assessments")
    
    def __repr__(self):
        return f"<Assessment {self.assessment_type} - {self.score}>"


class StudentCourse(Base):
    """Student course enrollments and grades"""
    __tablename__ = 'student_courses'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    semester_taken = Column(Integer)
    grade = Column(String(5))
    marks_obtained = Column(Integer, CheckConstraint('marks_obtained BETWEEN 0 AND 100'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="courses")
    course = relationship("Course", back_populates="student_courses")
    
    def __repr__(self):
        return f"<StudentCourse {self.student_id} - {self.course_id}: {self.grade}>"


class Project(Base):
    """Student projects"""
    __tablename__ = 'projects'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    project_title = Column(String(200), nullable=False)
    project_abstract = Column(Text)
    project_type = Column(String(30))
    semester = Column(Integer)
    tech_stack = Column(JSONB)
    document_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="projects")
    
    def __repr__(self):
        return f"<Project {self.project_title}>"


class Certification(Base):
    """Student certifications"""
    __tablename__ = 'certifications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    certification_title = Column(String(200), nullable=False)
    provider = Column(String(100))
    provider_credibility = Column(DECIMAL(3, 2), CheckConstraint('provider_credibility BETWEEN 0 AND 1'), default=0.7)
    completion_date = Column(Date)
    certificate_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="certifications")
    
    def __repr__(self):
        return f"<Certification {self.certification_title}>"


class Internship(Base):
    """Student internships"""
    __tablename__ = 'internships'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    company_name = Column(String(100))
    role_title = Column(String(100))
    duration_months = Column(Integer)
    description = Column(Text)
    skills_used = Column(JSONB)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="internships")
    
    def __repr__(self):
        return f"<Internship {self.company_name} - {self.role_title}>"


class User(Base):
    """System users (TPO, Faculty, Admin)"""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    full_name = Column(String(100))
    department = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<User {self.username} - {self.role}>"


class AuditLog(Base):
    """Audit trail for all system actions"""
    __tablename__ = 'audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(UUID(as_uuid=True))
    changes = Column(JSONB)
    ip_address = Column(INET)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AuditLog {self.action} at {self.created_at}>"


class SkillMappingOverride(Base):
    """Manual skill score overrides by faculty/admin"""
    __tablename__ = 'skill_mapping_overrides'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    original_score = Column(Integer)
    overridden_score = Column(Integer, CheckConstraint('overridden_score BETWEEN 0 AND 100'))
    overridden_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Override {self.student_id} - {self.skill_id}: {self.original_score} → {self.overridden_score}>"
