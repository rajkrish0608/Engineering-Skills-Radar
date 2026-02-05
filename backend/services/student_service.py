"""
Student CRUD Service
Handles all student-related database operations
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from models.database_models import Student, StudentSkill, StudentCourse, Project, Certification, Internship
from models.database_models import SkillAssessment, StudentRoleMatch


class StudentService:
    """Service for student CRUD operations"""
    
    @staticmethod
    def create_student(db: Session, student_data: Dict[str, Any]) -> Student:
        """
        Create a new student
        
        Args:
            db: Database session
            student_data: Student information dict
        
        Returns:
            Created Student object
        """
        student = Student(
            roll_number=student_data['roll_number'],
            full_name=student_data['full_name'],
            email=student_data['email'],
            branch=student_data['branch'],
            batch_year=student_data['batch_year'],
            current_semester=student_data.get('current_semester', 1),
            cgpa=student_data.get('cgpa', 0.0),
            account_status='active'
        )
        
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    
    @staticmethod
    def get_student_by_id(db: Session, student_id: uuid.UUID) -> Optional[Student]:
        """Get student by ID"""
        return db.query(Student).filter(Student.id == student_id).first()
    
    @staticmethod
    def get_student_by_roll(db: Session, roll_number: str) -> Optional[Student]:
        """Get student by roll number"""
        return db.query(Student).filter(Student.roll_number == roll_number).first()
    
    @staticmethod
    def get_students(
        db: Session,
        branch: Optional[str] = None,
        batch_year: Optional[int] = None,
        semester: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Student]:
        """
        Get students with optional filters
        
        Args:
            db: Database session
            branch: Filter by branch
            batch_year: Filter by batch year
            semester: Filter by semester
            skip: Pagination offset
            limit: Max results
        
        Returns:
            List of students
        """
        query = db.query(Student)
        
        if branch:
            query = query.filter(Student.branch == branch)
        if batch_year:
            query = query.filter(Student.batch_year == batch_year)
        if semester:
            query = query.filter(Student.current_semester == semester)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_student(
        db: Session,
        student_id: uuid.UUID,
        update_data: Dict[str, Any]
    ) -> Optional[Student]:
        """Update student information"""
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return None
        
        for key, value in update_data.items():
            if hasattr(student, key):
                setattr(student, key, value)
        
        student.updated_at = datetime.now()
        db.commit()
        db.refresh(student)
        return student
    
    @staticmethod
    def delete_student(db: Session, student_id: uuid.UUID) -> bool:
        """Delete student (and all related records via cascade)"""
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return False
        
        db.delete(student)
        db.commit()
        return True
    
    @staticmethod
    def get_student_skills(db: Session, student_id: uuid.UUID) -> List[StudentSkill]:
        """Get all skills for a student"""
        return db.query(StudentSkill).options(
            joinedload(StudentSkill.skill)
        ).filter(StudentSkill.student_id == student_id).all()
    
    @staticmethod
    def get_student_projects(db: Session, student_id: uuid.UUID) -> List[Project]:
        """Get all projects for a student"""
        return db.query(Project).filter(Project.student_id == student_id).all()
    
    @staticmethod
    def get_student_certifications(db: Session, student_id: uuid.UUID) -> List[Certification]:
        """Get all certifications for a student"""
        return db.query(Certification).filter(Certification.student_id == student_id).all()
    
    @staticmethod
    def get_student_role_matches(
        db: Session,
        student_id: uuid.UUID,
        top_n: int = 10
    ) -> List[StudentRoleMatch]:
        """
        Get top role matches for a student
        
        Args:
            db: Database session
            student_id: Student ID
            top_n: Number of top matches to return
        
        Returns:
            List of role matches sorted by match_score
        """
        return db.query(StudentRoleMatch).options(
            joinedload(StudentRoleMatch.role)
        ).filter(
            StudentRoleMatch.student_id == student_id
        ).order_by(
            StudentRoleMatch.match_score.desc()
        ).limit(top_n).all()
    
    @staticmethod
    def bulk_create_students(db: Session, students_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk create students from CSV import
        
        Returns:
            Statistics about import (success/failure counts)
        """
        success_count = 0
        failed_count = 0
        errors = []
        
        for student_data in students_data:
            try:
                # Check if already exists
                existing = db.query(Student).filter(
                    Student.roll_number == student_data['roll_number']
                ).first()
                
                if existing:
                    failed_count += 1
                    errors.append({
                        'roll_number': student_data['roll_number'],
                        'error': 'Student already exists'
                    })
                    continue
                
                # Create student
                StudentService.create_student(db, student_data)
                success_count += 1
            
            except Exception as e:
                failed_count += 1
                errors.append({
                    'roll_number': student_data.get('roll_number', 'unknown'),
                    'error': str(e)
                })
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'errors': errors
        }
    
    @staticmethod
    def search_students(
        db: Session,
        query: str,
        search_fields: List[str] = ['roll_number', 'full_name', 'email']
    ) -> List[Student]:
        """
        Search students by query string
        
        Args:
            db: Database session
            query: Search query
            search_fields: Fields to search in
        
        Returns:
            List of matching students
        """
        filters = []
        query_lower = f"%{query.lower()}%"
        
        if 'roll_number' in search_fields:
            filters.append(func.lower(Student.roll_number).like(query_lower))
        if 'full_name' in search_fields:
            filters.append(func.lower(Student.full_name).like(query_lower))
        if 'email' in search_fields:
            filters.append(func.lower(Student.email).like(query_lower))
        
        return db.query(Student).filter(or_(*filters)).limit(50).all()
